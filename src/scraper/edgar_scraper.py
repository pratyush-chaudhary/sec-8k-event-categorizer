"""Minimal SEC EDGAR scraper for downloading 8-K filings."""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests


@dataclass
class FilingInfo:
    """Information about a SEC filing."""
    
    cik: str
    company_name: str
    form: str
    filing_date: str
    accession_number: str
    document_url: str
    
    def get_filename(self) -> str:
        """Generate filename for the filing."""
        clean_accession = self.accession_number.replace("-", "")
        return f"{self.filing_date}_{clean_accession}_8k"
    
    def get_directory_name(self) -> str:
        """Generate directory name."""
        return f"{self.cik}_{self.get_filename()}"


class EdgarScraper:
    """Minimal scraper for SEC EDGAR database."""
    
    BASE_URL = "https://data.sec.gov"
    ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
    
    def __init__(self, user_agent: str = "Python SEC Scraper 1.0"):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Simple rate limiting."""
        current_time = time.time()
        if current_time - self.last_request_time < 0.1:  # 100ms between requests
            time.sleep(0.1)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> requests.Response:
        """Make rate-limited request."""
        self._rate_limit()
        response = self.session.get(url)
        response.raise_for_status()
        return response
    
    def get_company_submissions(self, cik: str) -> Dict:
        """Get company submissions from SEC."""
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"
        response = self._make_request(url)
        return response.json()
    
    def filter_8k_filings(self, submissions_data: Dict, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[FilingInfo]:
        """Filter 8-K filings from submissions."""
        filings = []
        recent = submissions_data.get("filings", {}).get("recent", {})
        
        if not recent:
            return filings
        
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        
        company_name = submissions_data.get("name", "Unknown")
        cik = str(submissions_data.get("cik", "")).zfill(10)
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        
        for i, form in enumerate(forms):
            if form == "8-K":
                filing_date = filing_dates[i]
                filing_dt = datetime.strptime(filing_date, "%Y-%m-%d")
                
                if start_dt and filing_dt < start_dt:
                    continue
                if end_dt and filing_dt > end_dt:
                    continue
                
                accession_number = accession_numbers[i]
                clean_accession = accession_number.replace("-", "")
                document_url = f"{self.ARCHIVES_URL}/{cik}/{clean_accession}/{accession_number}.txt"
                
                filing = FilingInfo(
                    cik=cik,
                    company_name=company_name,
                    form=form,
                    filing_date=filing_date,
                    accession_number=accession_number,
                    document_url=document_url
                )
                filings.append(filing)
        
        return filings
    
    def download_filing_content(self, filing_info: FilingInfo) -> str:
        """Download filing content."""
        response = self._make_request(filing_info.document_url)
        return response.text
    
    def scrape_8k_filings(self, cik: str, start_date: str, end_date: str) -> List[FilingInfo]:
        """Main scraping method."""
        self.logger.info(f"Scraping 8-K filings for CIK {cik}")
        
        # Get submissions
        submissions = self.get_company_submissions(cik)
        
        # Filter 8-K filings
        filings = self.filter_8k_filings(submissions, start_date, end_date)
        
        # Download content for each filing
        for filing in filings:
            try:
                content = self.download_filing_content(filing)
                filing._raw_content = content
            except Exception as e:
                self.logger.error(f"Error downloading {filing.accession_number}: {e}")
        
        self.logger.info(f"Found {len(filings)} 8-K filings")
        return filings 