"""
IDSP (Integrated Disease Surveillance Programme) Report Ingestion Script.

Fetches PDF reports from the MOHFW/IDSP portal, extracts disease data,
and persists records into the PRISM MongoDB cases_daily collection.

Usage:
    # Fetch from URL:
    python -m backend.scripts.ingest_idsp

    # Use a local PDF file if URL is blocked:
    python -m backend.scripts.ingest_idsp --local-file path/to/report.pdf
"""

import argparse
import io
import logging
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

# Suppress InsecureRequestWarning BEFORE any requests import
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import pdfplumber
import pdfplumber.utils.exceptions as pdfplumber_exc
import requests
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError, PyMongoError

# Ensure project root is on sys.path for backend.* imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db, ensure_indexes

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("idsp_ingestion")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT: int = 60

# Chrome UA — bypasses User-Agent blocking on government portals
BROWSER_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Canonical column names we want to extract (order-independent).
COLUMN_ALIASES: Dict[str, List[str]] = {
    "state":    ["state", "states", "state/ut", "state / ut"],
    "district": ["district", "districts", "dist"],
    "disease":  ["disease", "diseases", "illness", "condition"],
    "cases":    ["cases", "no. of cases", "no of cases", "number of cases",
                 "total cases", "reported cases"],
    "deaths":   ["deaths", "no. of deaths", "no of deaths", "number of deaths",
                 "total deaths", "reported deaths"],
    "date":     ["date", "week", "reported date", "date of reporting",
                 "reporting date", "report date"],
}

# Regex to strip anything that is not a digit or a minus sign.
_NON_NUMERIC_RE = re.compile(r"[^\d\-]")

# ---------------------------------------------------------------------------
# Region mapping — ISO 3166-2:IN
# ---------------------------------------------------------------------------
# Maps common IDSP state/UT spellings → PRISM region_id (IN-XX).
# Mirrors codes used across backend/utils/climate.py and seed_full.py.
STATE_TO_REGION_ID: Dict[str, str] = {
    "andhra pradesh":         "IN-AP",
    "arunachal pradesh":      "IN-AR",
    "assam":                  "IN-AS",
    "bihar":                  "IN-BR",
    "chhattisgarh":           "IN-CT",
    "goa":                    "IN-GA",
    "gujarat":                "IN-GJ",
    "haryana":                "IN-HR",
    "himachal pradesh":       "IN-HP",
    "jharkhand":              "IN-JH",
    "karnataka":              "IN-KA",
    "kerala":                 "IN-KL",
    "madhya pradesh":         "IN-MP",
    "maharashtra":            "IN-MH",
    "manipur":                "IN-MN",
    "meghalaya":              "IN-ML",
    "mizoram":                "IN-MZ",
    "nagaland":               "IN-NL",
    "odisha":                 "IN-OR",
    "punjab":                 "IN-PB",
    "rajasthan":              "IN-RJ",
    "sikkim":                 "IN-SK",
    "tamil nadu":             "IN-TN",
    "telangana":              "IN-TG",
    "tripura":                "IN-TR",
    "uttar pradesh":          "IN-UP",
    "uttarakhand":            "IN-UT",
    "west bengal":            "IN-WB",
    # Union territories
    "delhi":                  "IN-DL",
    "new delhi":              "IN-DL",
    "nct of delhi":           "IN-DL",
    "jammu & kashmir":        "IN-JK",
    "jammu and kashmir":      "IN-JK",
    "ladakh":                 "IN-LA",
    "chandigarh":             "IN-CH",
    "puducherry":             "IN-PY",
    "pondicherry":            "IN-PY",
    "andaman and nicobar":    "IN-AN",
    "andaman & nicobar":      "IN-AN",
    "dadra and nagar haveli": "IN-DN",
    "daman and diu":          "IN-DD",
    "lakshadweep":            "IN-LD",
}


def resolve_region_id(raw_state: str) -> str:
    """Map a raw state/UT string from the PDF to a PRISM region_id (IN-XX).

    Falls back to a generated code and emits a WARNING if the state is unknown,
    so the record is never silently dropped.
    """
    normalised = raw_state.strip().lower()
    if normalised in STATE_TO_REGION_ID:
        return STATE_TO_REGION_ID[normalised]
    # Partial / fuzzy fallback
    for key, region_id in STATE_TO_REGION_ID.items():
        if key in normalised or normalised in key:
            return region_id
    # Last-resort generated code
    clean = re.sub(r"[^a-zA-Z\s]", "", raw_state).strip().split()
    code = "XX" if not clean else (clean[0][:2] if len(clean) == 1 else (clean[0][0] + clean[1][0])).upper()
    generated = f"IN-{code}"
    logger.warning(
        "No region mapping for '%s' — using fallback '%s'. Add it to STATE_TO_REGION_ID.",
        raw_state, generated,
    )
    return generated


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------


def fetch_pdf_bytes(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[bytes]:
    """Fetch PDF bytes from *url* with browser-mimicking headers.

    Handles two scenarios:
    1. Direct PDF response (Content-Type: application/pdf).
    2. HTML wrapper page — scans for an embedded ``.pdf`` href and follows it once.

    SSL verification is disabled (``verify=False``) for government portals
    that use self-signed or expired certificates.
    """
    logger.info("Fetching: %s", url)
    try:
        response = requests.get(
            url,
            headers=BROWSER_HEADERS,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.exceptions.SSLError as exc:
        logger.error("SSL error (even with verify=False): %s", exc)
        return None
    except requests.exceptions.ConnectionError as exc:
        logger.error("Connection error — site may be down or blocking: %s", exc)
        return None
    except requests.exceptions.Timeout:
        logger.error("Request timed out after %ds", timeout)
        return None
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP %s: %s", response.status_code, exc)
        return None

    content_type = response.headers.get("Content-Type", "").lower()
    logger.info("Response — Content-Type: '%s' | Size: %s bytes", content_type, f"{len(response.content):,}")

    # Scenario 1: direct PDF
    if "application/pdf" in content_type or "application/octet-stream" in content_type:
        return response.content

    # Scenario 2: HTML wrapper — hunt for embedded PDF link
    if "text/html" in content_type:
        logger.info("HTML page received — scanning for embedded PDF link…")
        pdf_url = _extract_pdf_link_from_html(response.text, base_url=url)
        if pdf_url:
            logger.info("Found PDF link: %s — fetching…", pdf_url)
            return fetch_pdf_bytes(pdf_url, timeout=timeout)   # recurse once
        logger.error(
            "HTML page received but no PDF link found. "
            "The portal may require login or JavaScript rendering."
        )
        logger.debug("HTML snippet (first 500 chars):\n%s", response.text[:500])
        return None

    logger.error("Unexpected Content-Type '%s' — cannot parse as PDF.", content_type)
    return None


def _extract_pdf_link_from_html(html: str, base_url: str) -> Optional[str]:
    """Regex-scan HTML for an href ending in .pdf and return the absolute URL."""
    pattern = re.compile(r"""href=["']([^"']*\.pdf[^"']*)["']""", re.IGNORECASE)
    matches = pattern.findall(html)
    if not matches:
        logger.debug("No .pdf href found in HTML.")
        return None
    raw_link = matches[0]
    if raw_link.startswith(("http://", "https://")):
        return raw_link
    parsed = urlparse(base_url)
    return urljoin(f"{parsed.scheme}://{parsed.netloc}", raw_link)


# ---------------------------------------------------------------------------
# Table-parsing helpers
# ---------------------------------------------------------------------------

def _normalise_header(cell: Optional[str]) -> str:
    """Lower-case, strip whitespace/newlines from a header cell."""
    if cell is None:
        return ""
    return cell.lower().replace("\n", " ").strip()


def _clean_number(raw: Optional[str]) -> Optional[str]:
    """Strip commas, newlines, asterisks, footnote markers, and spaces."""
    if raw is None:
        return None
    cleaned = raw.replace("\n", "").replace(",", "").replace("*", "").strip()
    return cleaned if cleaned else None


def _to_int(raw: Optional[str], row_index: int, field: str) -> Optional[int]:
    """
    Safely convert a cleaned string to int.
    Logs a warning and returns None on failure instead of raising.
    """
    cleaned = _clean_number(raw)
    if cleaned is None or cleaned == "-" or cleaned.lower() in ("", "n/a", "na"):
        return None
    try:
        # Remove any remaining non-numeric characters (e.g. trailing citations)
        numeric_str = _NON_NUMERIC_RE.sub("", cleaned)
        return int(numeric_str) if numeric_str else None
    except ValueError:
        logger.warning(
            "Row %d — could not convert '%s' to int for field '%s'. Skipping field.",
            row_index, raw, field,
        )
        return None


def _map_columns(headers: List[Optional[str]]) -> Dict[str, int]:
    """
    Build a mapping of canonical column name → column index from a header row.
    Returns only the canonical columns that were successfully matched.
    """
    mapping: Dict[str, int] = {}
    for col_idx, raw_header in enumerate(headers):
        normalised = _normalise_header(raw_header)
        for canonical, aliases in COLUMN_ALIASES.items():
            if canonical in mapping:
                continue  # already found
            if any(alias in normalised for alias in aliases):
                mapping[canonical] = col_idx
                break
    return mapping


def _is_header_row(row: List[Optional[str]], col_map: Dict[str, int]) -> bool:
    """
    Detect repeated header rows that appear mid-table (common in IDSP PDFs
    where pages repeat the table header).
    """
    if not col_map:
        return False
    # If any mapped cell in this row matches a known alias, it's a header.
    for canonical, col_idx in col_map.items():
        cell = _normalise_header(row[col_idx]) if col_idx < len(row) else ""
        if any(alias in cell for alias in COLUMN_ALIASES[canonical]):
            return True
    return False


def _is_empty_row(row: List[Optional[str]]) -> bool:
    """Return True if every cell in the row is None or blank."""
    return all(not (cell or "").strip() for cell in row)


def _safe_get(row: List[Optional[str]], idx: int) -> Optional[str]:
    """Return row[idx] or None if index out of range."""
    if idx < 0 or idx >= len(row):
        return None
    return row[idx]


# ---------------------------------------------------------------------------
# PDF parsing
# ---------------------------------------------------------------------------


def parse_idsp_pdf(
    pdf_bytes: Optional[bytes] = None,
    local_file_path: Optional[str] = None,
) -> List[Dict]:
    """Extract disease case records from an IDSP PDF.

    Accepts either in-memory bytes (network fetch) or a local file path
    (offline testing) — exactly one must be supplied.
    """
    if not pdf_bytes and not local_file_path:
        raise ValueError("Provide either pdf_bytes or local_file_path.")

    records: List[Dict] = []
    try:
        if local_file_path:
            logger.info("Opening local PDF: %s", local_file_path)
            pdf_ctx = pdfplumber.open(local_file_path)
        else:
            logger.info("Opening in-memory PDF bytes…")
            pdf_ctx = pdfplumber.open(io.BytesIO(pdf_bytes))

        with pdf_ctx as pdf:
            logger.info("PDF opened — %d page(s).", len(pdf.pages))
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if not tables:
                    logger.debug("Page %d: no tables found, skipping.", page_num)
                    continue
                for table_idx, table in enumerate(tables):
                    if table:
                        records.extend(_process_table(table, page_num, table_idx))

    except pdfplumber_exc.PdfminerException as exc:
        logger.error("PDF structure error — corrupt or not a real PDF: %s", exc)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error while parsing PDF: %s", exc)

    logger.info("Extracted %d record(s) from PDF.", len(records))
    return records


# ---------------------------------------------------------------------------
# Database persistence
# ---------------------------------------------------------------------------


def save_to_database(records: List[Dict]) -> Dict[str, int]:
    """Bulk-upsert IDSP records into the PRISM ``cases_daily`` collection.

    Design:
    * Uses ``get_db()`` from ``backend.db`` — the single connection-pool source.
    * ``bulk_write`` with ``UpdateOne(upsert=True, $set)`` for idempotency and
      performance — re-running on the same PDF updates stale values rather than
      inserting duplicates.
    * Upsert filter: ``(region_id, date, disease)`` — matches the compound
      unique index defined in ``ensure_indexes()``.

    Returns a dict with ``upserted`` (new docs), ``modified`` (updated docs),
    and ``total`` (ops submitted) counts.
    """
    if not records:
        logger.warning("save_to_database called with empty records list — nothing to do.")
        return {"upserted": 0, "modified": 0, "total": 0}

    ensure_indexes()
    collection = get_db()["cases_daily"]
    bulk_ops: List[UpdateOne] = []

    for rec in records:
        # 1. Resolve region_id from state name
        region_id = resolve_region_id(rec.get("state") or rec.get("region_name", ""))

        # 2. Standardise disease to PRISM uppercase convention
        disease = (rec.get("disease") or "UNKNOWN").strip().upper()

        # 3. Normalise date to YYYY-MM-DD; fall back to today if malformed
        raw_date = rec.get("date") or ""
        try:
            datetime.strptime(raw_date, "%Y-%m-%d")
            standard_date = raw_date
        except ValueError:
            standard_date = date.today().strftime("%Y-%m-%d")
            logger.warning(
                "Malformed date '%s' for %s/%s — defaulting to %s",
                raw_date, region_id, disease, standard_date,
            )

        document = {
            "region_id":   region_id,
            "region_name": rec.get("state") or rec.get("region_name", ""),
            "district":    rec.get("district"),
            "date":        standard_date,
            "disease":     disease,
            "confirmed":   rec.get("cases") or rec.get("confirmed") or 0,
            "deaths":      rec.get("deaths") or 0,
            "recovered":   rec.get("recovered") or 0,
            "source":      "IDSP_PDF",
            "ingested_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        bulk_ops.append(
            UpdateOne(
                filter={"region_id": region_id, "date": standard_date, "disease": disease},
                update={"$set": document},
                upsert=True,
            )
        )

    upserted = modified = 0
    try:
        result = collection.bulk_write(bulk_ops, ordered=False)
        upserted = result.upserted_count
        modified = result.modified_count
        logger.info(
            "bulk_write complete — upserted (new): %d, modified (updated): %d, total ops: %d",
            upserted, modified, len(bulk_ops),
        )
    except BulkWriteError as bwe:
        upserted = bwe.details.get("nUpserted", 0)
        modified = bwe.details.get("nModified", 0)
        errors = bwe.details.get("writeErrors", [])
        logger.error(
            "BulkWriteError — partial write. upserted: %d, modified: %d, errors: %d",
            upserted, modified, len(errors),
        )
        for err in errors[:5]:
            logger.error("  Write error: %s", err)
    except PyMongoError as exc:
        logger.error("MongoDB error during bulk_write: %s", exc, exc_info=True)
        raise

    return {"upserted": upserted, "modified": modified, "total": len(bulk_ops)}


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def ingest_idsp_report(
    url: str = "https://idsp.mohfw.gov.in/showfile.php?lid=3915",
    local_file_path: Optional[str] = None,
) -> Dict[str, int]:
    """Full pipeline: fetch (or open locally) → parse → save to MongoDB."""
    pdf_bytes: Optional[bytes] = None

    if local_file_path:
        logger.info("Local-file mode — skipping network fetch.")
    else:
        pdf_bytes = fetch_pdf_bytes(url)
        if pdf_bytes is None:
            logger.error(
                "Could not retrieve PDF from network.\n"
                "TIP: Download the PDF manually and re-run with --local-file:\n"
                "  python -m backend.scripts.ingest_idsp --local-file path/to/report.pdf"
            )
            return {"records_parsed": 0, "db_upserted": 0, "db_modified": 0}

    records = parse_idsp_pdf(pdf_bytes=pdf_bytes, local_file_path=local_file_path)

    if not records:
        logger.warning(
            "PDF opened but no records extracted. "
            "Enable --debug and inspect extracted text to refine _process_table()."
        )
        return {"records_parsed": 0, "db_upserted": 0, "db_modified": 0}

    db_result = save_to_database(records)
    return {
        "records_parsed": len(records),
        "db_upserted":    db_result["upserted"],
        "db_modified":    db_result["modified"],
    }


# ---------------------------------------------------------------------------
# Table processing helper
# ---------------------------------------------------------------------------

def _process_table(
    table: List[List[Optional[str]]],
    page_num: int,
    table_idx: int,
) -> List[Dict]:
    """
    Process a single extracted table and return a list of clean record dicts.

    Parameters
    ----------
    table : List[List[Optional[str]]]
        Raw table data from pdfplumber (list of rows, each row a list of cells).
    page_num : int
        1-based page number (used only for logging).
    table_idx : int
        0-based table index on the page (used only for logging).

    Returns
    -------
    List[Dict]
    """
    records: List[Dict] = []
    col_map: Dict[str, int] = {}
    header_found: bool = False

    for row_idx, row in enumerate(table):
        # ----------------------------------------------------------------
        # Skip entirely empty rows
        # ----------------------------------------------------------------
        if _is_empty_row(row):
            continue

        # ----------------------------------------------------------------
        # Header detection — first non-empty row OR repeated header row
        # ----------------------------------------------------------------
        if not header_found:
            col_map = _map_columns(row)
            if col_map:
                header_found = True
                logger.debug(
                    "Page %d, Table %d: header detected at row %d → %s",
                    page_num, table_idx, row_idx, col_map,
                )
            else:
                logger.debug(
                    "Page %d, Table %d, Row %d: could not map columns — skipping row.",
                    page_num, table_idx, row_idx,
                )
            continue  # header row itself is not a data row

        # ----------------------------------------------------------------
        # Detect and skip repeated header rows mid-table
        # ----------------------------------------------------------------
        if _is_header_row(row, col_map):
            logger.debug(
                "Page %d, Table %d, Row %d: repeated header row — skipping.",
                page_num, table_idx, row_idx,
            )
            continue

        # ----------------------------------------------------------------
        # Extract and clean fields
        # ----------------------------------------------------------------
        try:
            raw_state    = _safe_get(row, col_map.get("state",    -1))
            raw_district = _safe_get(row, col_map.get("district", -1))
            raw_disease  = _safe_get(row, col_map.get("disease",  -1))
            raw_cases    = _safe_get(row, col_map.get("cases",    -1))
            raw_deaths   = _safe_get(row, col_map.get("deaths",   -1))
            raw_date     = _safe_get(row, col_map.get("date",     -1))

            # Normalise text fields
            state    = (raw_state or "").replace("\n", " ").strip() or None
            district = (raw_district or "").replace("\n", " ").strip() or None
            disease  = (raw_disease or "").replace("\n", " ").strip() or None
            date     = (raw_date or "").replace("\n", " ").strip() or None

            # Convert numeric fields
            global_row_id = f"p{page_num}t{table_idx}r{row_idx}"
            cases  = _to_int(raw_cases,  row_idx, f"{global_row_id}.cases")
            deaths = _to_int(raw_deaths, row_idx, f"{global_row_id}.deaths")

            # Skip rows where every extracted field is None (spurious rows)
            if not any([state, district, disease, cases, deaths, date]):
                logger.debug(
                    "Page %d, Table %d, Row %d: all fields empty — skipping.",
                    page_num, table_idx, row_idx,
                )
                continue

            record: Dict = {
                "state":    state,
                "district": district,
                "disease":  disease,
                "cases":    cases,
                "deaths":   deaths,
                "date":     date,
            }
            records.append(record)

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "Page %d, Table %d, Row %d: unexpected parse error — %s. Row skipped. Raw: %s",
                page_num, table_idx, row_idx, exc, row,
            )

    if not header_found:
        logger.warning(
            "Page %d, Table %d: no recognisable header found — table skipped entirely.",
            page_num, table_idx,
        )

    return records


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest IDSP disease surveillance PDF reports into PRISM."
    )
    parser.add_argument(
        "--url",
        default="https://idsp.mohfw.gov.in/showfile.php?lid=3915",
        help="URL of the IDSP PDF report (default: %(default)s)",
    )
    parser.add_argument(
        "--local-file",
        dest="local_file",
        default=None,
        help="Path to a locally saved PDF. Use when the URL is unreachable.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable DEBUG logging.",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    result = ingest_idsp_report(url=args.url, local_file_path=args.local_file)

    print("\n" + "=" * 60)
    print("IDSP Ingestion Summary")
    print("=" * 60)
    print(f"  Records parsed   : {result['records_parsed']}")
    print(f"  DB — new inserts : {result['db_upserted']}")
    print(f"  DB — updated     : {result['db_modified']}")
    print("=" * 60)

    if result["records_parsed"] == 0 and not args.local_file:
        print(
            "\n💡 If the URL was blocked, download the PDF manually:\n"
            f"   1. Open in browser: {args.url}\n"
            "   2. Save the file locally, e.g. downloads/idsp_report.pdf\n"
            "   3. Re-run:\n"
            "      python -m backend.scripts.ingest_idsp --local-file downloads/idsp_report.pdf\n"
        )
        sys.exit(1)
