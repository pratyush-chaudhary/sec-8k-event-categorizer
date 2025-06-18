"""Simple text extractor for 8-K filings using BeautifulSoup."""

import re
from bs4 import BeautifulSoup # type: ignore


class Filing8KTextExtractor:
    """Simple extractor to get clean text from 8-K HTML filings."""

    def __init__(self):
        # Tags to remove completely
        self.remove_tags = [
            "script",
            "style",
            "meta",
            "link",
            "head",
            "title",
            "nav",
            "noscript",
            "iframe",
            "button",
            "input",
            "img",
        ]

        # Boilerplate patterns to filter out
        self.noise_patterns = [
            r"SEC\.gov",
            r"EDGAR",
            r"Filing Detail",
            r"Document Format Files",
            r"Complete submission text file",
            r"XBRL.*DOCUMENT",
            r"Washington.*D\.?C\.?\s*20549",
            r"Securities and Exchange Commission",
            r"Form\s+8-K",
            r"Current Report",
            r"Commission File Number",
            r"Check the appropriate box",
            r"☐|☑|□|■",  # checkbox symbols
        ]

    def extract_from_html(self, html_content: str) -> str:
        """
        Extract clean text from HTML content.

        Args:
            html_content: Raw HTML content

        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove unwanted elements
        self._clean_soup(soup)

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

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
        for table in soup.find_all("table"):
            if table is None:  # Safety check
                continue
            table_text = table.get_text() or ""
            if any(
                pattern in table_text
                for pattern in ["Document Format Files", "Filing Detail", "tableFile", "Navigation"]
            ):
                table.decompose()

        # Remove divs with EDGAR-specific classes/ids
        for div in soup.find_all("div"):
            if div is None:  # Safety check
                continue
            div_id = div.get("id", "") or ""
            div_class = " ".join(div.get("class", []) or [])
            if any(
                identifier in f"{div_id} {div_class}"
                for identifier in ["header", "footer", "breadCrumb", "formDiv", "mailer"]
            ):
                div.decompose()

        # Remove empty elements after cleanup
        for _ in range(2):  # Multiple passes for nested empty tags
            for tag in soup.find_all():
                if tag.name and not tag.get_text(strip=True):
                    tag.decompose()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize the extracted text."""

        lines = text.split("\n")
        clean_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip lines with only special characters or numbers
            if re.match(r"^[\s\-_=*\.]+$", line) or re.match(r"^\d+$", line):
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
        result = "\n".join(clean_lines)

        # Remove excessive whitespace
        result = re.sub(r"\n{3,}", "\n\n", result)  # Max 2 consecutive newlines
        result = re.sub(r"[ \t]+", " ", result)  # Normalize spaces

        return result.strip()
