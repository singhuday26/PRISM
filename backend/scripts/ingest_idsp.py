"""
IDSP PDF Ingestion Script
--------------------------
Parses epidemiological data from Indian Government IDSP (Integrated Disease
Surveillance Programme) PDF reports.

Usage:
    python ingest_idsp.py

Author: PRISM Data Pipeline
"""

import io
import logging
import re
import sys
from typing import Dict, List, Optional

import pdfplumber
import pdfplumber.utils.exceptions as pdfplumber_exc
import requests

# ---------------------------------------------------------------------------
# Logging configuration
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
REQUEST_TIMEOUT: int = 60          # seconds
REQUEST_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PRISM-DataPipeline/1.0; "
        "+https://github.com/singhuday26/PRISM)"
    )
}

# Canonical column names we want to extract (order-independent).
# Each alias list covers common header variations found in IDSP PDFs.
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
# Helper utilities
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
# Core ingestion function
# ---------------------------------------------------------------------------

def ingest_idsp_report(pdf_url: str) -> List[Dict]:
    """
    Download an IDSP PDF report and extract structured epidemiological records.

    Parameters
    ----------
    pdf_url : str
        Publicly accessible URL of the IDSP PDF report.

    Returns
    -------
    List[Dict]
        Each dict contains the keys: state, district, disease, cases, deaths, date.
        Fields that could not be parsed are stored as None.
    """
    # ------------------------------------------------------------------
    # Step 1: Download PDF into an in-memory buffer
    # ------------------------------------------------------------------
    logger.info("Downloading PDF from: %s", pdf_url)
    try:
        response = requests.get(
            pdf_url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Request timed out after %ds for URL: %s", REQUEST_TIMEOUT, pdf_url)
        return []
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error %s while fetching: %s", exc.response.status_code, pdf_url)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("Failed to download PDF: %s", exc)
        return []

    content = response.content
    size_kb = len(content) / 1024
    logger.info("Download complete. Size: %.1f KB", size_kb)

    # ------------------------------------------------------------------
    # Validate that the response is actually a PDF
    # ------------------------------------------------------------------
    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower() and not content.startswith(b"%PDF"):
        # Log the first 500 bytes to help diagnose redirects / login walls
        preview = content[:500].decode("utf-8", errors="replace")
        logger.error(
            "Response is not a PDF (Content-Type: %s, size: %.1f KB). "
            "The server may require authentication or the URL may have changed.\n"
            "Response preview:\n%s",
            content_type, size_kb, preview,
        )
        return []

    pdf_buffer = io.BytesIO(content)

    # ------------------------------------------------------------------
    # Step 2: Parse PDF pages and extract tables
    # ------------------------------------------------------------------
    records: List[Dict] = []

    try:
        with pdfplumber.open(pdf_buffer) as pdf:
            logger.info("PDF opened. Total pages: %d", len(pdf.pages))

            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if not tables:
                    logger.debug("Page %d: no tables found, skipping.", page_num)
                    continue

                logger.debug("Page %d: found %d table(s).", page_num, len(tables))

                for table_idx, table in enumerate(tables):
                    if not table:
                        continue

                    page_records = _process_table(
                        table=table,
                        page_num=page_num,
                        table_idx=table_idx,
                    )
                    records.extend(page_records)

    except pdfplumber_exc.PdfminerException as exc:
        logger.error("PDF syntax/structure error — file may be corrupt or not a real PDF: %s", exc)
        return records
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error while parsing PDF: %s", exc)
        return records

    logger.info("Ingestion complete. Total records extracted: %d", len(records))
    return records


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
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TEST_URL = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"

    logger.info("=" * 60)
    logger.info("IDSP Report Ingestion — PRISM Data Pipeline")
    logger.info("=" * 60)

    extracted_records = ingest_idsp_report(TEST_URL)

    if not extracted_records:
        logger.warning("No records were extracted. Check the URL or PDF structure.")
        sys.exit(1)

    # Print a formatted summary to stdout
    print(f"\n{'=' * 60}")
    print(f"Extracted {len(extracted_records)} record(s)")
    print(f"{'=' * 60}")
    for i, rec in enumerate(extracted_records[:20], start=1):   # preview first 20
        print(
            f"[{i:>3}] state={rec['state']!r:20} district={rec['district']!r:20} "
            f"disease={rec['disease']!r:25} cases={rec['cases']} "
            f"deaths={rec['deaths']} date={rec['date']!r}"
        )
    if len(extracted_records) > 20:
        print(f"      ... and {len(extracted_records) - 20} more records.")
    print(f"{'=' * 60}\n")
