"""Minimal filing organizer for saving SEC filings."""

import json
import logging
from pathlib import Path
from typing import List

from .edgar_scraper import FilingInfo


class FilingOrganizer:
    """Simple organizer for SEC filings."""
    
    def __init__(self, data_dir: str = "data"):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def save_filing(self, filing_info: FilingInfo) -> Path:
        """Save a filing to organized directory structure."""
        
        # Create company directory
        company_dir = self.data_dir / filing_info.cik
        company_dir.mkdir(exist_ok=True)
        
        # Create filing directory
        filing_dir = company_dir / filing_info.get_directory_name()
        filing_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata = {
            "cik": filing_info.cik,
            "company_name": filing_info.company_name,
            "form": filing_info.form,
            "filing_date": filing_info.filing_date,
            "accession_number": filing_info.accession_number,
            "document_url": filing_info.document_url,
            "filename": filing_info.get_filename()
        }
        
        with open(filing_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save raw content if available
        if hasattr(filing_info, '_raw_content') and filing_info._raw_content:
            raw_file = filing_dir / f"{filing_info.get_filename()}.txt"
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(filing_info._raw_content)
        
        self.logger.info(f"Saved filing to {filing_dir}")
        return filing_dir
    
    def save_filings_batch(self, filings: List[FilingInfo]) -> List[Path]:
        """Save multiple filings."""
        saved_paths = []
        
        for i, filing in enumerate(filings, 1):
            try:
                path = self.save_filing(filing)
                saved_paths.append(path)
                self.logger.info(f"Progress: {i}/{len(filings)} filings saved")
            except Exception as e:
                self.logger.error(f"Error saving {filing.accession_number}: {e}")
        
        return saved_paths 