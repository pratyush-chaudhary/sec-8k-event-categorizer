# Python SEC 8-K Event Classifier & Scraper

A Python tool for downloading and classifying 8-K filing events using Large Language Models.

## Quick Start

### 1. Setup
```bash
git clone <repository-url>
cd python-sec-checker
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Classify a Single 8-K Filing
```python
from src.parser.event_classifier import EventClassifier
from src.parser.text_extractor import Filing8KTextExtractor

# Load your HTML filing content
with open("path/to/your/8k.html", "r") as f:
    html_content = f.read()

# Extract and classify
extractor = Filing8KTextExtractor()
clean_text = extractor.extract_from_html(html_content)

classifier = EventClassifier()
result = classifier.classify(clean_text)

print(f"Event Type: {result.event_type}")
print(f"Reasoning: {result.reasoning}")
```

### 3. Download & Classify Company Filings
```bash
# Download and classify Apple's last 30 days of 8-K filings
python scrape_and_categorize.py --company apple

# Download Tesla's filings without classification (faster)
python scrape_and_categorize.py --company tesla --no-classify

# List available companies
python scrape_and_categorize.py --list-companies
```

## Configuration

### 1. LLM Configuration
Create `config/llm_config.json`:
```json
{
  "provider": "ollama",
  "model": "llama3.1:8b", 
  "base_url": "http://localhost:11434",
  "temperature": 0.1,
  "max_tokens": 1000
}
```

### 2. Event Types Configuration  
Create `config/event_config.json`:
```json
{
  "Financial Event": {
    "relevant": true,
    "description": "Earnings, financial results, guidance",
    "keywords": ["earnings", "revenue", "profit", "guidance"]
  },
  "Corporate Action": {
    "relevant": true, 
    "description": "Mergers, acquisitions, spin-offs",
    "keywords": ["merger", "acquisition", "spinoff"]
  }
}
```

### 3. Install Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

## Output

Scraped filings are saved to `data/[CIK]/[filing_directory]/`:
- `metadata.json` - Filing metadata
- `[filename].txt` - Raw filing content
- `classification.json` - Event classification with reasoning 