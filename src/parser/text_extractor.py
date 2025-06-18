"""Simple text extractor for 8-K filings using BeautifulSoup."""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
from pathlib import Path


class Filing8KTextExtractor:
    """Simple extractor to get clean text from 8-K HTML filings."""
    
    def __init__(self):
        # Tags to remove completely
        self.remove_tags = [
            'script', 'style', 'meta', 'link', 'head', 'title', 
            'nav', 'noscript', 'iframe', 'button', 'input', 'img'
        ]
        
        # Boilerplate patterns to filter out
        self.noise_patterns = [
            r'SEC\.gov',
            r'EDGAR',
            r'Filing Detail',
            r'Document Format Files',
            r'Complete submission text file',
            r'XBRL.*DOCUMENT',
            r'Washington.*D\.?C\.?\s*20549',
            r'Securities and Exchange Commission',
            r'Form\s+8-K',
            r'Current Report',
            r'Commission File Number',
            r'Check the appropriate box',
            r'☐|☑|□|■',  # checkbox symbols
        ]
    
    def extract_from_file(self, file_path: str) -> str:
        """
        Extract clean text from an 8-K HTML file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Clean text content
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        return self.extract_from_html(html_content)
    
    def extract_from_html(self, html_content: str) -> str:
        """
        Extract clean text from HTML content.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        self._clean_soup(soup)
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean the text
        clean_text = self._clean_text(text)
        
        return clean_text
    
    def _clean_soup(self, soup: BeautifulSoup) -> None:
        """Remove unwanted tags and elements."""
        
        # Remove unwanted tags
        for tag_name in self.remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Remove tables that look like EDGAR navigation
        for table in soup.find_all('table'):
            if table is None:  # Safety check
                continue
            table_text = table.get_text() or ''
            if any(pattern in table_text for pattern in ['Document Format Files', 'Filing Detail', 'tableFile', 'Navigation']):
                table.decompose()
        
        # Remove divs with EDGAR-specific classes/ids
        for div in soup.find_all('div'):
            if div is None:  # Safety check
                continue
            div_id = div.get('id', '') or ''
            div_class = ' '.join(div.get('class', []) or [])
            if any(identifier in f"{div_id} {div_class}" for identifier in [
                'header', 'footer', 'breadCrumb', 'formDiv', 'mailer'
            ]):
                div.decompose()
        
        # Remove empty elements after cleanup
        for _ in range(2):  # Multiple passes for nested empty tags
            for tag in soup.find_all():
                if tag.name and not tag.get_text(strip=True):
                    tag.decompose()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the extracted text."""
        
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines with only special characters or numbers
            if re.match(r'^[\s\-_=*\.]+$', line) or re.match(r'^\d+$', line):
                continue
            
            # Skip short lines that are likely navigation/formatting
            if len(line) < 10:
                continue
            
            # Skip lines matching noise patterns
            is_noise = False
            for pattern in self.noise_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_noise = True
                    break
            
            if not is_noise:
                clean_lines.append(line)
        
        # Join lines and clean up spacing
        result = '\n'.join(clean_lines)
        
        # Remove excessive whitespace
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive newlines
        result = re.sub(r'[ \t]+', ' ', result)     # Normalize spaces
        
        return result.strip()
    
    def extract_key_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from the clean text for LLM processing.
        
        Args:
            text: Clean text content
            
        Returns:
            Dictionary with key sections
        """
        sections = {
            'full_text': text,
            'items': self._extract_items(text),
            'company_info': self._extract_company_info(text),
            'business_content': self._extract_business_content(text)
        }
        
        return sections
    
    def _extract_items(self, text: str) -> str:
        """Extract Item sections from the text."""
        
        # Look for Item X.XX patterns
        item_matches = re.findall(r'(Item\s+\d+\.\d+[^\n]+(?:\n[^\n]*)*?)(?=Item\s+\d+\.\d+|\n\n|\Z)', text, re.IGNORECASE)
        
        if item_matches:
            return '\n\n'.join(item_matches[:5])  # First 5 items
        
        return ""
    
    def _extract_company_info(self, text: str) -> str:
        """Extract company information."""
        
        # Look for company name patterns
        patterns = [
            r'([A-Z][a-zA-Z\s&.,]+(?:Inc\.?|Corp\.?|LLC|Company|Ltd\.?))',
            r'(Apple Inc\.?)',
            r'(\w+\s+Inc\.?\s+[^\n]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_business_content(self, text: str) -> str:
        """Extract the main business content, filtering out legal boilerplate."""
        
        lines = text.split('\n')
        business_lines = []
        
        # Look for substantive business content
        business_keywords = [
            'announced', 'reported', 'results', 'revenue', 'earnings', 'quarter',
            'performance', 'sales', 'growth', 'acquisition', 'merger', 'agreement',
            'product', 'service', 'customer', 'market', 'financial', 'dividend'
        ]
        
        for line in lines:
            # Include lines that contain business keywords
            if any(keyword in line.lower() for keyword in business_keywords):
                business_lines.append(line)
            # Include longer descriptive lines
            elif len(line) > 50 and not any(noise in line.lower() for noise in ['sec', 'edgar', 'commission']):
                business_lines.append(line)
        
        return '\n'.join(business_lines[:20])  # Limit to first 20 relevant lines


def main():
    """Test the text extractor with existing files."""
    
    extractor = Filing8KTextExtractor()
    
    print("=" * 60)
    print("8-K TEXT EXTRACTOR TEST")
    print("=" * 60)
    
    # Test with sample fixture
    print("\n1. Testing Sample Fixture")
    print("-" * 30)
    
    fixture_path = "tests/fixtures/sample_8k.html"
    if Path(fixture_path).exists():
        clean_text = extractor.extract_from_file(fixture_path)
        print(f"✓ Extracted {len(clean_text)} characters")
        print(f"Preview:\n{clean_text[:300]}...")
        
        # Extract key sections
        sections = extractor.extract_key_sections(clean_text)
        print(f"\nKey sections:")
        print(f"- Company: {sections['company_info']}")
        print(f"- Items: {sections['items'][:100]}...")
        print(f"- Business content: {sections['business_content'][:200]}...")
    else:
        print("✗ Sample fixture not found")
    
    # Test with downloaded Apple filing
    print("\n2. Testing Downloaded Apple Filing")
    print("-" * 35)
    
    import glob
    apple_files = glob.glob("data/320193/*/*.html")
    
    if apple_files:
        test_file = apple_files[0]
        print(f"Testing file: {test_file}")
        
        clean_text = extractor.extract_from_file(test_file)
        print(f"✓ Extracted {len(clean_text)} characters")
        print(f"Preview:\n{clean_text[:400]}...")
        
        # Extract key sections
        sections = extractor.extract_key_sections(clean_text)
        print(f"\nKey sections:")
        print(f"- Company: {sections['company_info']}")
        print(f"- Items: {sections['items'][:150]}...")
    else:
        print("✗ No Apple filing files found")


if __name__ == "__main__":
    main() 