#!/usr/bin/env python3
"""
Scrape and categorize 8-K filings with event classification.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from src.scraper import EdgarScraper, FilingOrganizer
from src.parser.event_classifier import PromptStrategy


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_popular_ciks():
    """Popular company CIKs."""
    return {
        "apple": "320193",
        "microsoft": "789019", 
        "amazon": "1018724",
        "tesla": "1318605",
        "nvidia": "1045810",
        "alphabet": "1652044",
        "meta": "1326801",
        "berkshire": "1067983",
        "jpmorgan": "19617",
        "visa": "1403161"
    }


def validate_date(date_string: str) -> str:
    """Validate date format."""
    try:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD.")


def main():
    parser = argparse.ArgumentParser(
        description="Download and classify 8-K filings from SEC EDGAR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and classify Apple's filings from last 30 days
  python scrape_and_categorize.py --company apple

  # Download without classification (faster)
  python scrape_and_categorize.py --company tesla --no-classify

  # Use different classification strategy
  python scrape_and_categorize.py --company microsoft --strategy cot

  # Custom date range
  python scrape_and_categorize.py --cik 320193 --start-date 2024-01-01 --end-date 2024-12-31
        """
    )
    
    # Company selection
    parser.add_argument("--cik", help="Company Central Index Key (CIK)")
    parser.add_argument("--company", choices=list(get_popular_ciks().keys()),
                       help="Popular company name")
    parser.add_argument("--list-companies", action="store_true",
                       help="List popular companies and their CIKs")
    
    # Date range
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days back from today (default: 30)")
    parser.add_argument("--start-date", type=validate_date,
                       help="Start date YYYY-MM-DD")
    parser.add_argument("--end-date", type=validate_date,
                       help="End date YYYY-MM-DD")
    
    # Classification options
    parser.add_argument("--no-classify", action="store_true",
                       help="Skip event classification (download only)")
    parser.add_argument("--strategy", choices=["basic", "detailed", "cot", "few_shot"],
                       default="detailed", help="Classification prompt strategy")
    
    # Configuration
    parser.add_argument("--llm-config", default="config/llm_config.json",
                       help="Path to LLM configuration file")
    parser.add_argument("--event-config", default="config/event_config.json",
                       help="Path to event configuration file")
    
    # Output options
    parser.add_argument("--data-dir", default="extracted_events",
                       help="Base directory to save filings and classifications (will create CIK subdirectory)")
    parser.add_argument("--user-agent", 
                       default="Python SEC Scraper 1.0",
                       help="User agent for SEC requests")
    
    # Other options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be downloaded without downloading")
    
    args = parser.parse_args()
    
    # Show companies list
    if args.list_companies:
        print("\nPopular companies:")
        print("-" * 40)
        for name, cik in get_popular_ciks().items():
            print(f"  {name.capitalize():<12}: {cik}")
        print()
        return 0
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Determine CIK
    if args.company:
        cik = get_popular_ciks()[args.company]
        logger.info(f"Using CIK {cik} for {args.company.capitalize()}")
    elif args.cik:
        cik = args.cik
    else:
        print("Error: Must specify either --cik or --company")
        print("Use --list-companies to see available options")
        return 1
    
    # Determine date range
    if args.start_date:
        start_date = args.start_date
        end_date = args.end_date or datetime.now().strftime("%Y-%m-%d")
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    logger.info(f"Date range: {start_date} to {end_date}")
    
    try:
        # Initialize scraper
        logger.info("Initializing SEC EDGAR scraper...")
        scraper = EdgarScraper(user_agent=args.user_agent)
        
        # Get filings
        logger.info(f"Fetching 8-K filings for CIK {cik}...")
        filings = scraper.scrape_8k_filings(cik, start_date, end_date)
        
        if not filings:
            logger.info("No 8-K filings found for the specified criteria")
            return 0
        
        print(f"\nFound {len(filings)} 8-K filings:")
        print("-" * 60)
        for filing in filings:
            print(f"  {filing.filing_date} - {filing.accession_number}")
        
        if args.dry_run:
            classify_msg = "with classification" if not args.no_classify else "without classification"
            print(f"\nDry run complete. Would download {len(filings)} filings {classify_msg}.")
            print(f"Target directory: {Path(args.data_dir) / cik}")
            return 0
        
        # Initialize organizer with classification settings
        logger.info("Initializing filing organizer...")
        strategy_map = {
            "basic": PromptStrategy.BASIC,
            "detailed": PromptStrategy.DETAILED,
            "cot": PromptStrategy.CHAIN_OF_THOUGHT,
            "few_shot": PromptStrategy.FEW_SHOT
        }
        
        # Create CIK-specific subdirectory under extracted_events
        cik_data_dir = str(Path(args.data_dir) / cik)
        
        organizer = FilingOrganizer(
            data_dir=cik_data_dir,
            llm_config_path=args.llm_config,
            event_config_path=args.event_config,
            classify_events=not args.no_classify,
            prompt_strategy=strategy_map[args.strategy]
        )
        
        # Process filings
        logger.info("Processing filings...")
        saved_paths = organizer.save_filings_batch(filings)
        
        # Print summary
        print(f"\nProcessing completed!")
        print(f"Successfully processed: {len(saved_paths)}/{len(filings)} filings")
        print(f"Data directory: {Path(cik_data_dir).absolute()}")
        
        if not args.no_classify:
            print(f"Classification strategy: {args.strategy}")
            print("\nEach filing directory contains:")
            print("  - metadata.json (filing metadata)")
            print("  - [filename].txt (raw filing content)")
            print("  - classification.json (event classification)")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 