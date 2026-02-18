import pdfplumber
import requests
import logging
from typing import List, Dict
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_idsp_report(pdf_url: str) -> List[Dict]:
    logging.info(f"Starting to ingest IDSP report from URL: {pdf_url}")
    data = []

    try:
        # Download the PDF
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)

        with pdfplumber.open(pdf_file) as pdf:
            for page_number in range(len(pdf.pages)):
                page = pdf.pages[page_number]
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        if row[0] == "Sr. No":  # Skip header row
                            continue
                        try:
                            state = row[1].strip()
                            district = row[2].strip()
                            disease = row[3].strip()
                            cases = int(row[4].replace(',', '').strip())
                            deaths = int(row[5].replace(',', '').strip())
                            date = row[6].strip()

                            # Append cleaned data to the list
                            data.append({
                                "state": state,
                                "district": district,
                                "disease": disease,
                                "cases": cases,
                                "deaths": deaths,
                                "date": date
                            })
                        except (ValueError, IndexError) as e:
                            logging.error(f"Error parsing row {row}: {e}")

    except requests.RequestException as e:
        logging.error(f"Failed to download PDF: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    logging.info("Data ingestion completed.")
    return data

if __name__ == "__main__":
    sample_url = "https://idsp.mohfw.gov.in/showfile.php?lid=3915"
    report_data = ingest_idsp_report(sample_url)
    for entry in report_data:
        print(entry)