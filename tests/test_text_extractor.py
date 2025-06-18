#!/usr/bin/env python3
"""Test suite for 8-K text extractor."""

import sys
import os
import unittest
import glob
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.text_extractor import Filing8KTextExtractor


class TestFiling8KTextExtractor(unittest.TestCase):
    """Test cases for Filing8KTextExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = Filing8KTextExtractor()
        
    def test_extract_from_sample_fixture(self):
        """Test text extraction with sample 8-K fixture."""
        print("\n--- Testing sample fixture text extraction ---")
        
        fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_8k.html")
        
        if os.path.exists(fixture_path):
            clean_text = self.extractor.extract_from_file(fixture_path)
            
            # Should extract substantial text
            self.assertGreater(len(clean_text), 100)
            
            # Should contain business content
            self.assertIn('Apple', clean_text)
            
            # Should NOT contain common noise
            self.assertNotIn('SEC.gov', clean_text)
            self.assertNotIn('EDGAR', clean_text)
            
            print(f"✓ Extracted {len(clean_text)} characters")
            print(f"Preview: {clean_text[:150]}...")
            
        else:
            self.skipTest("Sample fixture not found")
    
    def test_extract_from_downloaded_filing(self):
        """Test text extraction with downloaded Apple filing."""
        print("\n--- Testing downloaded filing text extraction ---")
        
        # Find Apple filing files
        apple_files = glob.glob("data/320193/*/*.html")
        
        if apple_files:
            test_file = apple_files[0]
            print(f"Testing with: {test_file}")
            
            clean_text = self.extractor.extract_from_file(test_file)
            
            # Should extract some text
            self.assertGreater(len(clean_text), 0)
            
            print(f"✓ Extracted {len(clean_text)} characters")
            print(f"Preview: {clean_text[:200]}...")
            
        else:
            self.skipTest("No Apple filing files found")
    
    def test_key_sections_extraction(self):
        """Test extraction of key sections."""
        print("\n--- Testing key sections extraction ---")
        
        # Test with sample content
        test_text = """
        Apple Inc. announced quarterly results for Q4 2024.
        
        Item 2.02 Results of Operations and Financial Condition
        
        The company reported revenue of $100 billion for the quarter.
        Item 9.01 Financial Statements and Exhibits
        
        Performance was strong across all product categories.
        """
        
        sections = self.extractor.extract_key_sections(test_text)
        
        self.assertIn('full_text', sections)
        self.assertIn('items', sections)
        self.assertIn('company_info', sections)
        self.assertIn('business_content', sections)
        
        # Should extract company name
        self.assertEqual(sections['company_info'], 'Apple Inc.')
        
        # Should extract items
        self.assertIn('Item 2.02', sections['items'])
        self.assertIn('Item 9.01', sections['items'])
        
        # Should extract business content
        self.assertIn('revenue', sections['business_content'])
        
        print(f"✓ Company: {sections['company_info']}")
        print(f"✓ Items: {sections['items'][:100]}...")
        print(f"✓ Business content: {sections['business_content'][:100]}...")
    
    def test_noise_filtering(self):
        """Test filtering of SEC/EDGAR boilerplate."""
        print("\n--- Testing noise filtering ---")
        
        noisy_html = """
        <html>
        <body>
        <div id="header">SEC.gov</div>
        <p>EDGAR Filing Detail</p>
        <script>console.log('test');</script>
        <p>This is important business content about Apple Inc.</p>
        <p>Washington, D.C. 20549</p>
        <p>Apple announced quarterly earnings results.</p>
        <table class="tableFile">Navigation table</table>
        </body>
        </html>
        """
        
        clean_text = self.extractor.extract_from_html(noisy_html)
        
        # Should contain business content
        self.assertIn('important business content', clean_text)
        self.assertIn('quarterly earnings', clean_text)
        
        # Should NOT contain noise
        self.assertNotIn('SEC.gov', clean_text)
        self.assertNotIn('EDGAR', clean_text)
        self.assertNotIn('Washington, D.C.', clean_text)
        self.assertNotIn('Navigation table', clean_text)
        
        print(f"✓ Filtered text: {clean_text}")


def test_manual():
    """Manual test function for detailed output."""
    print("=" * 60)
    print("MANUAL TEST: 8-K Text Extractor")
    print("=" * 60)
    
    extractor = Filing8KTextExtractor()
    
    # Test 1: Sample fixture
    print("\n1. Testing Sample Fixture")
    print("-" * 30)
    
    fixture_path = "tests/fixtures/sample_8k.html"
    if os.path.exists(fixture_path):
        clean_text = extractor.extract_from_file(fixture_path)
        sections = extractor.extract_key_sections(clean_text)
        
        print(f"✓ Extracted {len(clean_text)} characters")
        print(f"✓ Company: {sections['company_info']}")
        print(f"✓ Items found: {len(sections['items'])} chars")
        print(f"✓ Business content: {len(sections['business_content'])} chars")
        
        print(f"\nClean text preview:")
        print("-" * 40)
        print(clean_text[:500])
        print("-" * 40)
        
    else:
        print("✗ Sample fixture not found")
    
    # Test 2: Downloaded Apple filings
    print("\n2. Testing Downloaded Apple Filings")
    print("-" * 35)
    
    apple_files = glob.glob("data/320193/*/*.html")
    if apple_files:
        for i, file_path in enumerate(apple_files[:2]):  # Test first 2 files
            print(f"\nFile {i+1}: {file_path}")
            
            try:
                clean_text = extractor.extract_from_file(file_path)
                sections = extractor.extract_key_sections(clean_text)
                
                print(f"  Extracted: {len(clean_text)} characters")
                print(f"  Company: {sections['company_info'] or 'Not found'}")
                print(f"  Items: {len(sections['items'])} chars")
                print(f"  Business: {len(sections['business_content'])} chars")
                
                if clean_text:
                    print(f"  Preview: {clean_text[:200]}...")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
    else:
        print("✗ No Apple filing files found")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run manual test for detailed output
    test_manual()
    
    print("\nRUNNING UNIT TESTS")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2) 