"""Filing organizer with event classification for saving SEC filings."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from .edgar_scraper import FilingInfo
from ..parser.event_classifier import EventClassifier, PromptStrategy
from ..parser.text_extractor import Filing8KTextExtractor


class FilingOrganizer:
    """Organizer for SEC filings with event classification."""
    
    def __init__(self, 
                 data_dir: str = "data",
                 llm_config_path: str = "config/llm_config.json",
                 event_config_path: str = "config/event_config.json",
                 classify_events: bool = True,
                 prompt_strategy: PromptStrategy = PromptStrategy.DETAILED):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.classify_events = classify_events
        
        # Initialize classification components
        if classify_events:
            try:
                self.classifier = EventClassifier(
                    llm_config_path=llm_config_path,
                    event_config_path=event_config_path
                )
                self.text_extractor = Filing8KTextExtractor()
                self.prompt_strategy = prompt_strategy
                self.logger.info("Event classification enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize classifier: {e}")
                self.classify_events = False
        
    def save_filing(self, filing_info: FilingInfo) -> Path:
        """Save a filing with optional event classification."""
        
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
            
            # Perform event classification
            if self.classify_events:
                self._classify_and_save(filing_info, filing_dir)
        
        self.logger.info(f"Saved filing to {filing_dir}")
        return filing_dir
    
    def _classify_and_save(self, filing_info: FilingInfo, filing_dir: Path):
        """Classify filing and save classification results."""
        try:
            # Extract clean text for classification
            if hasattr(filing_info, '_raw_content'):
                clean_text = self.text_extractor.extract_from_html(filing_info._raw_content)
                
                # Classify the filing
                self.logger.info(f"Classifying filing {filing_info.accession_number}")
                classification_result = self.classifier.classify(
                    text=clean_text,
                    strategy=self.prompt_strategy
                )
                
                if classification_result:
                    # Save classification results
                    classification_data = {
                        "accession_number": filing_info.accession_number,
                        "event_type": classification_result.event_type,
                        "relevant": classification_result.relevant,
                        "reasoning": classification_result.reasoning,
                        "confidence": getattr(classification_result, 'confidence', None),
                        "prompt_strategy": self.prompt_strategy.value,
                        "classification_timestamp": filing_info.filing_date
                    }
                    
                    classification_file = filing_dir / "classification.json"
                    with open(classification_file, "w") as f:
                        json.dump(classification_data, f, indent=2)
                    
                    self.logger.info(f"Classification saved: {classification_result.event_type} (relevant: {classification_result.relevant})")
                else:
                    self.logger.warning(f"Classification failed for {filing_info.accession_number}")
                    
        except Exception as e:
            self.logger.error(f"Error during classification: {e}")
    
    def save_filings_batch(self, filings: List[FilingInfo]) -> List[Path]:
        """Save multiple filings with classification."""
        saved_paths = []
        
        for i, filing in enumerate(filings, 1):
            try:
                path = self.save_filing(filing)
                saved_paths.append(path)
                self.logger.info(f"Progress: {i}/{len(filings)} filings processed")
            except Exception as e:
                self.logger.error(f"Error saving {filing.accession_number}: {e}")
        
        return saved_paths 