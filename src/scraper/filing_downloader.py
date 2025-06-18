"""Clean, minimalistic 8-K filing downloader for SEC EDGAR database."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


class Filing8KDownloader:
    """Downloads 8-K filings from SEC EDGAR for a given CIK and date range."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.base_url = "https://www.sec.gov"
        self.headers = {
            "User-Agent": "SEC Filing Downloader (your-email@example.com)",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_8k_filings(self, cik: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Get list of 8-K filings for a CIK within date range.
        
        Args:
            cik: Company CIK (e.g., "320193" for Apple)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of filing dictionaries with metadata
        """
        # SEC EDGAR company filings URL
        url = f"{self.base_url}/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": cik,
            "type": "8-K",
            "dateb": end_date.replace("-", ""),  # SEC expects YYYYMMDD
            "datea": start_date.replace("-", ""),
            "owner": "exclude",
            "output": "atom",  # Get XML feed
            "count": "100"  # Max filings per request
        }
        
        print(f"Fetching 8-K filings for CIK {cik} from {start_date} to {end_date}...")
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            time.sleep(0.5)  # Be respectful to SEC servers
            
            # Parse XML feed
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')
            
            filings = []
            for entry in entries:
                filing_date = entry.find('filing-date').text if entry.find('filing-date') else None
                filing_href = entry.find('filing-href').text if entry.find('filing-href') else None
                accession_number = entry.find('accession-nunber').text if entry.find('accession-nunber') else None
                
                if filing_date and filing_href:
                    filings.append({
                        'cik': cik,
                        'filing_date': filing_date,
                        'accession_number': accession_number,
                        'filing_url': filing_href,
                        'document_url': self._get_document_url(filing_href)
                    })
            
            print(f"Found {len(filings)} 8-K filings")
            return filings
            
        except requests.RequestException as e:
            print(f"Error fetching filings: {e}")
            return []
    
    def _get_document_url(self, filing_href: str) -> str:
        """Convert filing href to actual document URL."""
        # filing_href is like: /Archives/edgar/data/320193/000119312521328151/0001193125-21-328151-index.htm
        # We want the actual 8-K document, typically ending in 8k.htm or similar
        
        # Extract path components
        path_parts = filing_href.split('/')
        if len(path_parts) >= 5:
            cik = path_parts[4]
            accession = path_parts[5]
            
            # Try common 8-K document naming patterns
            accession_clean = accession.replace('-', '')
            possible_names = [
                f"d{accession_clean[-6:]}8k.htm",  # Common pattern: d259993d8k.htm
                f"{accession_clean}8k.htm",
                f"form8k.htm",
                f"8k.htm"
            ]
            
            for name in possible_names:
                doc_url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession}/{name}"
                return doc_url
        
        return filing_href  # Fallback to original URL
    
    def download_filing(self, filing: Dict) -> Optional[str]:
        """
        Download a single 8-K filing.
        
        Args:
            filing: Filing dictionary with metadata
            
        Returns:
            Path to downloaded file or None if failed
        """
        cik = filing['cik']
        filing_date = filing['filing_date']
        accession = filing['accession_number']
        
        # Create directory structure: data/CIK/YYYY/
        year = filing_date[:4]
        filing_dir = self.data_dir / cik / year
        filing_dir.mkdir(parents=True, exist_ok=True)
        
        # Filename: YYYY-MM-DD_accession_8k.html
        filename = f"{filing_date}_{accession}_8k.html"
        filepath = filing_dir / filename
        
        # Skip if already downloaded
        if filepath.exists():
            print(f"Already exists: {filename}")
            return str(filepath)
        
        # Try to download the actual 8-K document
        doc_url = filing['document_url']
        
        try:
            print(f"Downloading: {filename}")
            response = self.session.get(doc_url, timeout=30)
            
            if response.status_code == 404:
                # Try alternative URL patterns
                print(f"404 error, trying filing URL: {filing['filing_url']}")
                response = self.session.get(filing['filing_url'], timeout=30)
            
            response.raise_for_status()
            
            # Save the HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Save metadata
            metadata = {
                'cik': cik,
                'filing_date': filing_date,
                'accession_number': accession,
                'download_date': datetime.now().isoformat(),
                'source_url': doc_url,
                'filename': filename
            }
            
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            time.sleep(0.5)  # Be respectful to SEC servers
            return str(filepath)
            
        except requests.RequestException as e:
            print(f"Error downloading {filename}: {e}")
            return None
    
    def download_filings_bulk(self, cik: str, start_date: str, end_date: str) -> List[str]:
        """
        Download all 8-K filings for a CIK within date range.
        
        Args:
            cik: Company CIK
            start_date: Start date in YYYY-MM-DD format  
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of paths to downloaded files
        """
        filings = self.get_8k_filings(cik, start_date, end_date)
        downloaded_files = []
        
        for filing in filings:
            filepath = self.download_filing(filing)
            if filepath:
                downloaded_files.append(filepath)
        
        print(f"Successfully downloaded {len(downloaded_files)} filings")
        return downloaded_files
    
    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()


def main():
    """Example usage for downloading Apple 8-K filings."""
    downloader = Filing8KDownloader()
    
    # Download Apple 8-K filings from 2023
    apple_cik = "320193"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    try:
        downloaded_files = downloader.download_filings_bulk(
            cik=apple_cik,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\nDownloaded {len(downloaded_files)} files:")
        for file in downloaded_files[:5]:  # Show first 5
            print(f"  {file}")
        
        if len(downloaded_files) > 5:
            print(f"  ... and {len(downloaded_files) - 5} more")
            
    finally:
        downloader.close()


if __name__ == "__main__":
    main() 