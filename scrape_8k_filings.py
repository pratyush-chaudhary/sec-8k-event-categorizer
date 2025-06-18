#!/usr/bin/env python3
"""
Minimal CLI script for downloading 8-K filings.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta

from src.scraper import EdgarScraper, FilingOrganizer


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_popular_ciks():
    """Popular company CIKs."""
    return {
        "apple": "320193",
        "microsoft": "789019", 
        "amazon": "1018724",
        "tesla": "1318605",
        "nvidia": "1045810"
    }


def main():
    parser = argparse.ArgumentParser(description="Download 8-K filings from SEC")
    
    # Company selection
    parser.add_argument("--cik", help="Company CIK")
    parser.add_argument("--company", choices=list(get_popular_ciks().keys()),
                       help="Popular company name")
    
    # Date range
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days back from today (default: 30)")
    parser.add_argument("--start-date", help="Start date YYYY-MM-DD")
    parser.add_argument("--end-date", help="End date YYYY-MM-DD")
    
    # Options
    parser.add_argument("--data-dir", default="data", help="Data directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded")
    parser.add_argument("--list-companies", action="store_true", help="List popular companies")
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Show companies
    if args.list_companies:
        print("\nPopular companies:")
        for name, cik in get_popular_ciks().items():
            print(f"  {name}: {cik}")
        return
    
    # Determine CIK
    if args.company:
        cik = get_popular_ciks()[args.company]
    elif args.cik:
        cik = args.cik
    else:
        print("Error: Specify --cik or --company")
        return 1
    
    # Determine date range
    if args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    try:
        # Initialize scraper
        scraper = EdgarScraper()
        
        # Get filings
        logger.info(f"Fetching 8-K filings for CIK {cik} from {start_date} to {end_date}")
        filings = scraper.scrape_8k_filings(cik, start_date, end_date)
        
        if not filings:
            print("No 8-K filings found")
            return
        
        print(f"\nFound {len(filings)} 8-K filings:")
        for filing in filings:
            print(f"  {filing.filing_date} - {filing.accession_number}")
        
        if args.dry_run:
            print(f"\nDry run complete. Would download {len(filings)} filings.")
            return
        
        # Save filings
        organizer = FilingOrganizer(data_dir=args.data_dir)
        saved_paths = organizer.save_filings_batch(filings)
        
        print(f"\nSaved {len(saved_paths)}/{len(filings)} filings to {args.data_dir}/")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 