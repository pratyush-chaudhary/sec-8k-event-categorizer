# Python SEC 8-K Event Classifier & Scraper

A Python tool for downloading and classifying 8-K filing events using Large Language Models with advanced prompt engineering techniques.

## Key Command to Get Started

```bash
# Quick start: Download and classify Tesla's 8-K filings from the last 30 days
python scrape_and_categorize.py --company tesla

# To see example results, check the extracted_events directory
ls -la extracted_events/
```

## Installation & Setup

```bash
git clone https://github.com/pratyush-chaudhary/sec-8k-event-categorizer
cd sec-8k-event-categorizer
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Example Results

Check the `extracted_events/` directory to see example classification results with detailed reasoning and confidence scores. Each filing includes:
- Event type classification 
- Relevance assessment
- Detailed reasoning with Chain-of-Thought analysis
- Confidence scores
- Classification timestamps

## Usage Examples

### 1. Classify a Single 8-K Filing
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
print(f"Confidence: {result.confidence}")
```

### 2. Download & Classify Company Filings
```bash
# Download and classify Apple's last 30 days of 8-K filings
python scrape_and_categorize.py --company apple

# Download Tesla's filings without classification (faster)
python scrape_and_categorize.py --company tesla --no-classify

# List available companies
python scrape_and_categorize.py --list-companies
```

### 3. Use Different Prompt Strategies
```python
from src.parser.event_classifier import EventClassifier, PromptStrategy

classifier = EventClassifier()

# Chain-of-Thought prompting for better reasoning
result = classifier.classify(text, strategy=PromptStrategy.CHAIN_OF_THOUGHT)

# Few-shot learning with examples
result = classifier.classify(text, strategy=PromptStrategy.FEW_SHOT)

# Basic classification
result = classifier.classify(text, strategy=PromptStrategy.BASIC)
```

## Configuration

### 1. LLM Configuration
Create `config/llm_config.json`:
```json
{
  "provider": "ollama",
  "model": "gemma3:latest",
  "options": {
    "temperature": 0.7,
    "timeout": 30
  }
}
```

### 2. Event Types Configuration  
Create `config/event_config.json`:
```json
{
  "Acquisition": {
    "relevant": true,
    "description": "Mergers, acquisitions, asset purchases, or business combinations",
    "keywords": ["acquisition", "merger", "purchase", "acquire", "bought", "deal", "takeover"]
  },
  "Customer Event": {
    "relevant": true,
    "description": "Major customer contracts, partnerships, or customer-related announcements",
    "keywords": ["contract", "partnership", "customer", "agreement", "deal", "alliance"]
  },
  "Personnel Change": {
    "relevant": true,
    "description": "Changes in executive leadership, board members, or key personnel",
    "keywords": ["CEO", "CFO", "president", "director", "appointment", "resignation", "departure", "hire"]
  },
  "Financial Event": {
    "relevant": true,
    "description": "Earnings announcements, dividend declarations, financial results",
    "keywords": ["earnings", "results", "revenue", "profit", "dividend", "financial", "quarterly"]
  },
  "Regulatory/Legal Event": {
    "relevant": true,
    "description": "Legal proceedings, SEC investigations, regulatory approvals/denials, compliance issues",
    "keywords": ["lawsuit", "litigation", "SEC", "investigation", "regulatory", "compliance", "violation", "settlement", "FDA approval", "patent"]
  },
  "Corporate Restructuring": {
    "relevant": true,
    "description": "Spin-offs, divestitures, bankruptcies, reorganizations, subsidiary sales",
    "keywords": ["spin-off", "divestiture", "bankruptcy", "restructuring", "subsidiary", "reorganization", "liquidation"]
  },
  "Capital Market Event": {
    "relevant": true,
    "description": "Stock offerings, debt issuance, credit agreements, share buybacks, dividend changes",
    "keywords": ["offering", "debt", "credit agreement", "buyback", "repurchase", "bond", "loan", "financing", "dividend"]
  },
  "Product/Service Event": {
    "relevant": true,
    "description": "Major product launches, recalls, regulatory approvals (especially pharma/biotech)",
    "keywords": ["product launch", "recall", "FDA", "approval", "drug", "clinical trial", "patent approval"]
  },
  "Strategic Alliance": {
    "relevant": true,
    "description": "Joint ventures, strategic partnerships, licensing deals (broader than customer events)",
    "keywords": ["joint venture", "strategic partnership", "licensing", "collaboration", "alliance", "technology transfer"]
  },
  "Scheduling Event": {
    "relevant": false,
    "description": "Scheduled events like earnings calls, meetings, or conferences",
    "keywords": ["schedule", "meeting", "conference", "call", "date", "announce"]
  },
  "Other": {
    "relevant": false,
    "description": "Events that don't fit into other categories",
    "keywords": []
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

## Output Structure

Scraped filings are saved to `extracted_events/[CIK]/[filing_directory]/`:
- `metadata.json` - Filing metadata (CIK, accession number, dates)
- `classification.json` - Event classification with detailed reasoning and confidence
- Raw filing content preserved for analysis

## Prompt Engineering & Optimization Approaches

This project implements several advanced prompt engineering techniques to improve classification accuracy and reasoning quality:

### 1. Chain-of-Thought (CoT) Prompting

Our CoT implementation breaks down the classification process into three structured steps:

**Step 1: Identify Key Facts**
- Extract specific events being reported
- Identify parties involved
- Assess financial/business implications

**Step 2: Match to Category**  
- Evaluate fit against each category
- Provide comparative reasoning
- Justify category selection

**Step 3: Assess Significance**
- Evaluate material impact potential
- Consider investor relevance
- Distinguish routine vs. exceptional events

This approach significantly improves reasoning quality and classification accuracy compared to zero-shot prompting.

### 2. Few-Shot Learning with Domain Examples

We provide curated examples of well-classified 8-K events across different categories:
- Acquisition announcements with financial details
- Earnings results with growth metrics  
- Executive appointments with strategic context

Each example includes both the classification and detailed reasoning, helping the model understand the expected output format and reasoning depth.

### 3. Detailed Prompt Engineering

Our detailed prompts include:
- **Context Setting**: Positioning the LLM as a financial analyst expert
- **Clear Instructions**: Step-by-step classification guidance
- **Relevance Criteria**: Explicit definition of what makes events material
- **Output Structure**: Consistent formatting for parsing and validation

### 4. Multi-Strategy Validation

We implement multiple prompt strategies and can validate results:
- **Basic**: Simple category matching
- **Detailed**: Rich context with event descriptions and keywords
- **CoT**: Step-by-step reasoning process
- **Few-Shot**: Learning from examples

### 5. Output Validation Logic

**LLM-Based Validation**:
- Secondary validation prompts to check classification consistency
- Cross-validation between different prompt strategies
- Confidence scoring based on reasoning quality

**Python-Based Validation**:
- Schema validation for output structure
- Keyword matching against event configurations
- Relevance scoring using configurable criteria
- Retry logic with different strategies on parsing failures

### 6. Extensible Architecture

The prompt system is designed for easy extension:
- **Template-Based**: All prompts use configurable templates
- **Strategy Pattern**: Easy to add new prompt strategies
- **Config-Driven**: Event types and criteria defined in JSON
- **Modular Validation**: Separate validation logic for different aspects

### Areas for Improvement & Future Research

**1. Dynamic Prompt Optimization**
- A/B testing different prompt variations
- Automated prompt optimization based on performance metrics
- Context-aware prompt selection based on filing characteristics

**2. Enhanced Validation Pipeline**
- Multi-model consensus validation
- Historical performance tracking for continuous improvement
- Automated feedback loops from classification results

**3. Domain-Specific Improvements**
- Industry-specific event type expansion
- Sector-aware classification with specialized prompts
- Integration with financial databases for enhanced context

**4. Advanced Prompt Techniques**
- Self-consistency checking with multiple generations
- Tool-assisted reasoning with financial calculators
- Multi-step verification processes for high-stakes classifications

**5. Performance & Scalability**
- Batch processing optimization for large datasets
- Caching strategies for similar filings
- Distributed processing for enterprise-scale deployment

This implementation demonstrates that thoughtful prompt engineering combined with robust validation can significantly improve LLM performance on domain-specific classification tasks. The modular architecture allows for rapid experimentation with new techniques while maintaining production reliability. 