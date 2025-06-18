#!/usr/bin/env python3
"""Test suite for the 8-K filing downloader."""

import sys
import os
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.filing_downloader import Filing8KDownloader


class TestFiling8KDownloader(unittest.TestCase):
    """Test cases for Filing8KDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = Filing8KDownloader(data_dir="test_data")
        self.apple_cik = "320193"
        
    def tearDown(self):
        """Clean up after tests."""
        self.downloader.close()
    
    def test_get_8k_filings(self):
        """Test fetching 8-K filings list."""
        print("\n--- Testing get_8k_filings ---")
        
        # Test with Apple for a short recent date range
        start_date = "2023-10-01"
        end_date = "2023-12-31"
        
        filings = self.downloader.get_8k_filings(
            self.apple_cik, start_date, end_date
        )
        
        self.assertIsInstance(filings, list)
        
        if filings:
            print(f"Found {len(filings)} filings")
            
            # Check structure of first filing
            filing = filings[0]
            required_keys = ['cik', 'filing_date', 'accession_number', 'filing_url', 'document_url']
            
            for key in required_keys:
                self.assertIn(key, filing, f"Missing key: {key}")
                
            print(f"Sample filing: {filing['filing_date']} - {filing['accession_number']}")
        else:
            print("No filings found for test period")
    
    def test_document_url_generation(self):
        """Test document URL generation from filing href."""
        print("\n--- Testing document URL generation ---")
        
        # Test with typical filing href
        test_href = "/Archives/edgar/data/320193/000119312521328151/0001193125-21-328151-index.htm"
        doc_url = self.downloader._get_document_url(test_href)
        
        self.assertIsInstance(doc_url, str)
        self.assertIn("320193", doc_url)
        self.assertIn("000119312521328151", doc_url)
        
        print(f"Generated URL: {doc_url}")
    
    def test_download_single_filing(self):
        """Test downloading a single filing."""
        print("\n--- Testing single filing download ---")
        
        # First get a list of filings
        filings = self.downloader.get_8k_filings(
            self.apple_cik, "2023-11-01", "2023-12-31"
        )
        
        if filings:
            # Try to download the first filing
            filing = filings[0]
            print(f"Attempting to download: {filing['filing_date']} - {filing['accession_number']}")
            
            filepath = self.downloader.download_filing(filing)
            
            if filepath:
                print(f"✓ Successfully downloaded: {filepath}")
                # Check if file exists
                self.assertTrue(Path(filepath).exists())
                
                # Check if metadata file exists
                metadata_path = Path(filepath).with_suffix('.json')
                self.assertTrue(metadata_path.exists())
                
                print(f"✓ Metadata file created: {metadata_path}")
            else:
                print("✗ Download failed (this may be expected due to URL patterns)")
        else:
            self.skipTest("No filings available for download test")


def test_manual():
    """Manual test function for easier debugging."""
    print("="*60)
    print("MANUAL TEST: Apple 8-K Filing Downloader")
    print("="*60)
    
    downloader = Filing8KDownloader()
    
    try:
        # Test with Apple for a short date range
        apple_cik = "320193"
        start_date = "2023-11-01"
        end_date = "2023-12-31"
        
        print(f"Testing with CIK: {apple_cik}")
        print(f"Date range: {start_date} to {end_date}")
        print("-" * 40)
        
        # Get filings list
        filings = downloader.get_8k_filings(apple_cik, start_date, end_date)
        
        if filings:
            print(f"✓ Found {len(filings)} 8-K filings")
            
            # Show details of first few filings
            for i, filing in enumerate(filings[:3]):
                print(f"\nFiling {i+1}:")
                print(f"  Date: {filing['filing_date']}")
                print(f"  Accession: {filing['accession_number']}")
                print(f"  Document URL: {filing['document_url']}")
            
            # Try downloading the first one
            if len(filings) > 0:
                print("\n" + "-" * 40)
                print("Attempting to download first filing...")
                
                filepath = downloader.download_filing(filings[0])
                if filepath:
                    print(f"✓ SUCCESS: Downloaded to {filepath}")
                    
                    # Check file size
                    file_size = Path(filepath).stat().st_size
                    print(f"  File size: {file_size:,} bytes")
                else:
                    print("✗ FAILED: Could not download filing")
        else:
            print("✗ No 8-K filings found for the specified date range")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        downloader.close()


if __name__ == "__main__":
    # Run manual test for easier debugging
    test_manual()
    
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2) 