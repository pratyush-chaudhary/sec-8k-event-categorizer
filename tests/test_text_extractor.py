#!/usr/bin/env python3
"""Test suite for 8-K text extractor."""

import sys
import os
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.text_extractor import Filing8KTextExtractor


class TestFiling8KTextExtractor(unittest.TestCase):
    """Test cases for Filing8KTextExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = Filing8KTextExtractor()
        
    def test_extract_from_html_basic(self):
        """Test basic HTML text extraction."""
        print("\n--- Testing basic HTML extraction ---")
        
        # Simple HTML content
        html_content = """
        <html>
        <body>
        <p>This is important business content about Apple Inc.</p>
        <p>Apple announced quarterly earnings results for Q4 2024.</p>
        <p>Revenue increased by 10% compared to last quarter.</p>
        </body>
        </html>
        """
        
        clean_text = self.extractor.extract_from_html(html_content)
        
        # Should extract business content
        self.assertIn('important business content', clean_text)
        self.assertIn('quarterly earnings', clean_text)
        self.assertIn('Revenue increased', clean_text)
        
        print(f"✓ Extracted text: {clean_text}")
    
    def test_noise_filtering(self):
        """Test filtering of SEC/EDGAR boilerplate."""
        print("\n--- Testing noise filtering ---")
        
        noisy_html = """
        <html>
        <head><title>SEC Filing</title></head>
        <body>
        <div id="header">SEC.gov</div>
        <p>EDGAR Filing Detail</p>
        <script>console.log('test');</script>
        <p>This is important business content about Apple Inc.</p>
        <p>Washington, D.C. 20549</p>
        <p>Apple announced quarterly earnings results.</p>
        <table class="tableFile">Navigation table</table>
        <meta name="description" content="SEC filing">
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

    def test_empty_html(self):
        """Test handling of empty or minimal HTML."""
        print("\n--- Testing empty HTML handling ---")
        
        # Empty HTML
        empty_html = "<html><body></body></html>"
        clean_text = self.extractor.extract_from_html(empty_html)
        self.assertEqual(clean_text, "")
        
        # HTML with only noise
        noise_only_html = """
        <html>
        <head><title>SEC.gov</title></head>
        <body>
        <script>console.log('noise');</script>
        <p>EDGAR Filing Detail</p>
        </body>
        </html>
        """
        clean_text = self.extractor.extract_from_html(noise_only_html)
        self.assertEqual(clean_text, "")
        
        print("✓ Empty HTML handled correctly")

    def test_complex_html_structure(self):
        """Test extraction from complex HTML structure."""
        print("\n--- Testing complex HTML structure ---")
        
        complex_html = """
        <html>
        <head>
            <title>Apple Inc. 8-K Filing</title>
            <meta name="description" content="SEC filing">
        </head>
        <body>
            <header>
                <nav>Navigation menu</nav>
            </header>
            <div id="content">
                <h1>Apple Inc. Current Report</h1>
                <div class="section">
                    <h2>Item 2.02 Results of Operations and Financial Condition</h2>
                    <p>Apple Inc. ("Apple" or the "Company") today announced financial results for its fiscal 2023 fourth quarter ended September 30, 2023.</p>
                    <p>The Company posted quarterly revenue of $89.5 billion and quarterly earnings per diluted share of $1.46.</p>
                </div>
                <div class="section">
                    <h2>Forward-Looking Statements</h2>
                    <p>This Current Report on Form 8-K contains forward-looking statements within the meaning of the Private Securities Litigation Reform Act of 1995.</p>
                </div>
            </div>
            <footer>
                <p>© 2023 Apple Inc. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        
        clean_text = self.extractor.extract_from_html(complex_html)
        
        # Should extract business content
        self.assertIn('Apple Inc.', clean_text)
        self.assertIn('financial results', clean_text)
        self.assertIn('quarterly revenue', clean_text)
        self.assertIn('Item 2.02', clean_text)
        
        # Should not contain navigation or footer noise
        self.assertNotIn('Navigation menu', clean_text)
        
        print(f"✓ Complex structure handled: {len(clean_text)} characters")
        print(f"Preview: {clean_text[:200]}...")


if __name__ == "__main__":
    unittest.main(verbosity=2) 