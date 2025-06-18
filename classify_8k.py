#!/usr/bin/env python3
"""
End-to-end 8-K filing classification script.

This script demonstrates the complete pipeline:
1. Load and extract text from 8-K HTML filings
2. Classify events using LLM
3. Display results

Usage:
    python classify_8k.py [file_path] [--strategy STRATEGY]
"""

import sys
import argparse
import logging
import requests
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from src.parser.text_extractor import Filing8KTextExtractor
from src.parser.event_classifier import EventClassifier, PromptStrategy

# SEC access configuration
HEADERS = {"User-Agent": "about@plux.ai"}


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def is_url(input_string: str) -> bool:
    """Check if input string is a URL."""
    try:
        result = urlparse(input_string)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def download_filing_content(url: str) -> str:
    """
    Download 8-K filing content from URL.
    
    Args:
        url: SEC EDGAR URL to download
        
    Returns:
        HTML content as string
        
    Raises:
        requests.RequestException: If download fails
    """
    # Add a small delay to be respectful to SEC servers
    time.sleep(1)
    
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    
    return response.text


def classify_8k_filing(
    input_source: str, 
    strategy: PromptStrategy = PromptStrategy.DETAILED,
    verbose: bool = False
) -> Optional[dict]:
    """
    Complete pipeline: extract text and classify 8-K filing.
    
    Args:
        input_source: Path to 8-K HTML file or URL to SEC filing
        strategy: Prompt strategy to use
        verbose: Enable verbose logging
        
    Returns:
        Dictionary with results or None if failed
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Get HTML content (from file or URL)
        if is_url(input_source):
            logger.info(f"Downloading content from: {input_source}")
            html_content = download_filing_content(input_source)
            source_type = "URL"
        else:
            logger.info(f"Reading file: {input_source}")
            with open(input_source, 'r', encoding='utf-8') as f:
                html_content = f.read()
            source_type = "File"
        
        # Step 2: Extract text from HTML
        logger.info(f"Extracting text from {source_type.lower()}")
        extractor = Filing8KTextExtractor()
        extracted_text = extractor.extract_from_html(html_content)
        
        if not extracted_text:
            logger.error("No text extracted from filing")
            return None
        
        logger.info(f"Extracted {len(extracted_text)} characters")
        if verbose:
            logger.debug(f"Sample text: {extracted_text[:200]}...")
        
        # Step 3: Classify the event
        logger.info(f"Classifying event using {strategy.value} strategy")
        classifier = EventClassifier()
        
        result = classifier.classify(extracted_text, strategy=strategy)
        
        if not result:
            logger.error("Classification failed")
            return None
        
        # Step 4: Prepare results
        logger.info("Classification successful!")
        
        return {
            'input_source': input_source,
            'source_type': source_type,
            'strategy': strategy.value,
            'text_length': len(extracted_text),
            'extracted_text': extracted_text,
            'classification': {
                'event_type': result.event_type,
                'relevant': result.relevant,
                'confidence': result.confidence,
                'reasoning': result.reasoning,
                'raw_response': result.raw_response
            }
        }
        
    except FileNotFoundError:
        logger.error(f"File not found: {input_source}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error downloading from URL: {e}")
        if "403" in str(e) or "Forbidden" in str(e):
            logger.info("SEC.gov blocks automated access. Try:")
            logger.info("   1. Download the filing manually and use the local file")
            logger.info("   2. Use a different SEC EDGAR access method")
            logger.info("   3. Check SEC's data access guidelines")
        return None
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if verbose:
            logger.exception("Full traceback:")
        return None


def print_results(results: dict):
    """Print classification results in a nice format."""
    print("\n" + "="*60)
    print("8-K FILING CLASSIFICATION RESULTS")
    print("="*60)
    
    print(f"Source: {results['input_source']}")
    print(f"Strategy: {results['strategy']}")
    print(f"Text Length: {results['text_length']:,} characters")
    print()
    
    classification = results['classification']
    
    print("CLASSIFICATION:")
    print(f"   Event Type: {classification['event_type']}")
    print(f"   Relevant: {'Yes' if classification['relevant'] else 'No'}")
    print(f"   Confidence: {classification['confidence']:.1%}")
    
    if classification['reasoning']:
        print(f"\nREASONING:")
        print(f"   {classification['reasoning']}")
    
    print(f"\nRAW LLM RESPONSE:")
    print(f"   {classification['raw_response']}")
    
    print("\n" + "="*60)


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(
        description="Classify 8-K filing events using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local files
  python classify_8k.py tests/fixtures/sample_8k.html
  python classify_8k.py data/320193/2024/2024-02-01_None_8k.html --strategy basic
  
  # SEC EDGAR URLs  
  python classify_8k.py "https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm"
  python classify_8k.py "https://www.sec.gov/Archives/edgar/data/320193/000032019324000005/aapl-20240201.htm" --strategy cot
        """
    )
    
    parser.add_argument(
        'input_source',
        nargs='?',
        default='tests/fixtures/sample_8k.html',
        help='Path to 8-K HTML file or SEC EDGAR URL (default: tests/fixtures/sample_8k.html)'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['basic', 'detailed', 'cot', 'few_shot'],
        default='detailed',
        help='Prompt strategy to use (default: detailed)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--list-files',
        action='store_true',
        help='List available 8-K files and exit'
    )
    
    args = parser.parse_args()
    
    # List available files
    if args.list_files:
        print("Available 8-K files:")
        print("\nTest fixtures:")
        print("  tests/fixtures/sample_8k.html")
        
        print("\nDownloaded Apple filings:")
        data_dir = Path("data/320193")
        if data_dir.exists():
            for year_dir in sorted(data_dir.iterdir()):
                if year_dir.is_dir():
                    print(f"\n  {year_dir.name}:")
                    for file_path in sorted(year_dir.glob("*.html")):
                        print(f"    {file_path}")
        return
    
    # Convert strategy string to enum
    strategy_map = {
        'basic': PromptStrategy.BASIC,
        'detailed': PromptStrategy.DETAILED,
        'cot': PromptStrategy.CHAIN_OF_THOUGHT,
        'few_shot': PromptStrategy.FEW_SHOT
    }
    strategy = strategy_map[args.strategy]
    
    # Check if input is valid (file exists or is URL)
    if not is_url(args.input_source) and not Path(args.input_source).exists():
        print(f"Error: File not found: {args.input_source}")
        print("\nUse --list-files to see available files or provide a valid SEC URL")
        sys.exit(1)
    
    print("Starting 8-K classification pipeline...")
    print(f"Source: {args.input_source}")
    print(f"Strategy: {args.strategy}")
    
    # Run the classification
    results = classify_8k_filing(args.input_source, strategy, args.verbose)
    
    if results:
        print_results(results)
        print("\nClassification completed successfully!")
    else:
        print("\nClassification failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 