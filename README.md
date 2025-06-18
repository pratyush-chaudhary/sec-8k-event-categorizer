# SEC Form 8-K Event Classification System

## Assignment Overview

This project implements an intelligent system for automatically downloading, processing, and classifying SEC Form 8-K filings using Large Language Models (LLMs). The system analyzes corporate event disclosures, categorizes them by event type, and determines their significance for investors.

## What is Form 8-K?

Form 8-K is a regulatory filing that publicly traded companies must submit to the SEC within four business days of triggering events. These "current reports" disclose material corporate events that shareholders should know about, including:

- **Corporate Actions**: Mergers, acquisitions, spin-offs
- **Leadership Changes**: CEO/CFO departures, board changes  
- **Financial Events**: Earnings announcements, dividend declarations
- **Business Developments**: Major contracts, partnerships, legal settlements
- **Operational Changes**: Facility closures, restructuring announcements

## Problem Statement

### Core Challenge
Manual analysis of 8-K filings is time-intensive and requires domain expertise. This system automates the process by:

1. **Automated Data Collection**: Downloading 8-K filings from SEC EDGAR database
2. **Intelligent Classification**: Using LLMs to categorize event types
3. **Significance Assessment**: Determining investor relevance of disclosed events
4. **Flexible Configuration**: Supporting user-defined event taxonomies
5. **Quality Validation**: Testing against ground-truth examples

### Business Value
- **Investment Research**: Rapid screening of material events across portfolios
- **Risk Management**: Early detection of significant corporate changes
- **Compliance Monitoring**: Systematic tracking of regulatory disclosures
- **Market Analysis**: Understanding event patterns and their market impact

## Technical Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Processing      │    │   Intelligence  │
│                 │    │     Layer        │    │     Layer       │
│ • SEC EDGAR API │───▶│ • Text Extraction│───▶│ • LLM Integration│
│ • Filing Cache  │    │ • Preprocessing  │    │ • Prompt Engine │
│ • Ground Truth  │    │ • Section Parser │    │ • Classification │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration & Evaluation                   │
│                                                                 │
│ • Event Type Definitions    • Relevance Criteria               │
│ • Prompt Templates         • Performance Metrics               │
│ • Ground Truth Validation  • Quality Assurance                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Technologies
- **Python 3.8+**: Core application framework
- **Ollama**: Local LLM deployment and inference
- **BeautifulSoup4**: HTML parsing and text extraction
- **Requests**: HTTP client for SEC data retrieval
- **Pandas**: Data manipulation and analysis
- **JSON/YAML**: Configuration and output formatting

## Prompt Engineering Strategy

### Multi-Layered Approach

#### 1. Zero-Shot Classification
Basic prompt template for initial classification without examples:
```
Analyze this SEC Form 8-K filing and classify the primary event disclosed.

Event Categories: [Acquisition, Personnel Change, Customer Event, Financial Event, Other]

Provide classification in JSON format with reasoning.
```

#### 2. Chain-of-Thought (CoT) Reasoning
Structured thinking process to improve accuracy:
```
Analyze this 8-K filing step-by-step:

Step 1: Identify the key business event described
Step 2: Extract relevant entities (companies, people, amounts)  
Step 3: Assess the event's potential market impact
Step 4: Classify event type based on analysis
Step 5: Determine significance level with justification

REASONING:
[Your detailed step-by-step analysis including:
- Key facts identified from the filing
- Category matching rationale
- Significance assessment
- Final justification]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]
```

#### 3. Few-Shot Learning
Include relevant examples to guide classification:
```
Here are examples of classified 8-K events:

Example 1: "Apple announces acquisition of Beats Electronics for $3B"
Classification: {"event_type": "Acquisition", "relevant": true, "confidence": 0.95}

Example 2: "Microsoft CFO to step down effective next quarter"  
Classification: {"event_type": "Personnel Change", "relevant": true, "confidence": 0.90}

Now classify this filing: [TARGET_TEXT]
```

#### 4. Multi-Step Validation
Implement consistency checks and confidence scoring:
- **Format Validation**: Ensure JSON output compliance
- **Category Validation**: Verify against allowed event types
- **Confidence Thresholding**: Flag low-confidence predictions
- **Cross-Validation**: Multiple model consensus

## Configuration System

### Event Type Definition
Users define event taxonomies via JSON configuration:

```json
{
  "event_types": {
    "Acquisition": {
      "relevant": true,
      "keywords": ["acquire", "merger", "purchase", "buy"],
      "significance_threshold": 0.7
    },
    "Personnel Change": {
      "relevant": true, 
      "keywords": ["resign", "retire", "appoint", "CEO", "CFO"],
      "significance_threshold": 0.6
    },
    "Customer Event": {
      "relevant": true,
      "keywords": ["contract", "agreement", "partnership"],
      "significance_threshold": 0.5
    },
    "Financial Event": {
      "relevant": true,
      "keywords": ["earnings", "dividend", "buyback"],
      "significance_threshold": 0.8
    },
    "Other": {
      "relevant": false,
      "keywords": [],
      "significance_threshold": 0.3
    }
  },
  "relevance_criteria": {
    "market_cap_threshold": 1000000000,
    "revenue_impact_threshold": 0.05,
    "strategic_importance": ["core_business", "new_market", "technology"]
  }
}
```

### Ground Truth Format
Testing dataset for validation:

```json
{
  "ground_truth": [
    {
      "filing_url": "https://www.sec.gov/Archives/edgar/data/320193/...",
      "expected_classification": {
        "event_type": "Acquisition",
        "relevant": true,
        "confidence": 0.95
      },
      "notes": "Apple acquires AI startup for $200M"
    }
  ]
}
```

## Implementation Phases

### Phase 1: Foundation (MVP)
- [ ] SEC filing downloader with error handling
- [ ] Basic text extraction and cleaning
- [ ] Simple LLM integration via Ollama
- [ ] JSON output formatting
- [ ] CLI interface

### Phase 2: Intelligence (Core)
- [ ] Advanced prompt engineering (CoT, few-shot)
- [ ] Multi-model validation framework
- [ ] Confidence scoring and uncertainty quantification
- [ ] Configuration-driven event taxonomies
- [ ] Ground truth evaluation system

### Phase 3: Production (Advanced)
- [ ] Batch processing capabilities
- [ ] Caching and performance optimization
- [ ] Comprehensive logging and monitoring
- [ ] Error recovery and retry logic
- [ ] API interface for integration

### Phase 4: Enhancement (Future)
- [ ] Real-time filing monitoring
- [ ] Market data integration for impact assessment
- [ ] Fine-tuned domain-specific models
- [ ] Multi-modal analysis (tables, charts)
- [ ] Temporal pattern analysis

## Quality Assurance

### Validation Framework
- **Accuracy Metrics**: Precision, recall, F1-score by event type
- **Consistency Testing**: Multiple runs with same input
- **Edge Case Handling**: Malformed filings, ambiguous events
- **Performance Benchmarking**: Latency, throughput measurements

### Error Analysis
- **False Positives**: Events misclassified as significant
- **False Negatives**: Significant events missed or downgraded  
- **Category Confusion**: Events assigned to wrong types
- **Confidence Calibration**: Alignment between confidence and accuracy

## Research Extensions

### Areas for Investigation
1. **Prompt Optimization**: Automated prompt tuning and A/B testing
2. **Domain Adaptation**: Fine-tuning on financial text corpora
3. **Multi-Modal Processing**: Analyzing financial tables and exhibits
4. **Temporal Modeling**: Understanding event sequences and context
5. **Market Integration**: Correlating classifications with stock movements
6. **Regulatory Evolution**: Adapting to changing disclosure requirements

### Performance Improvements
- **Model Ensemble**: Combining multiple LLM outputs
- **Active Learning**: Iterative ground truth expansion
- **Transfer Learning**: Leveraging pre-trained financial models
- **Distillation**: Creating smaller, faster specialized models

## Getting Started

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a suitable model
ollama pull llama2
# or
ollama pull mistral
```

### Installation
```bash
# Clone repository
git clone [repository-url]
cd python-sec-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run with default configuration
python main.py --company AAPL --limit 5

# Use custom configuration
python main.py --config custom_config.json --company AAPL

# Evaluate against ground truth
python main.py --evaluate --ground-truth ground_truth.json
```

## Success Metrics

### Technical Metrics
- **Classification Accuracy**: >85% on ground truth dataset
- **Processing Speed**: <30 seconds per filing
- **System Reliability**: 99%+ uptime for batch processing
- **Output Quality**: 100% valid JSON formatting

### Business Metrics  
- **Coverage**: Successfully process 95%+ of target filings
- **Relevance**: 90%+ agreement with expert classifications
- **Timeliness**: Process filings within 1 hour of availability
- **Extensibility**: Support new event types without code changes

---

*This system demonstrates advanced LLM prompt engineering, production-ready Python development, and practical financial technology applications.* 