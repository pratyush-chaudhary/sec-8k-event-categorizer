# 8-K Filing Classification - Usage Guide

This guide shows how to use the end-to-end classification system.

## Quick Start

### 1. Demo (No LLM Required)
Test the pipeline without making actual LLM calls:

```bash
python demo_classify_8k.py
```

This shows the complete pipeline working with mock classification results.

### 2. Real Classification (Requires LLM)
Classify actual filings using your configured LLM:

```bash
# Default: Use test fixture with detailed strategy
python classify_8k.py

# Classify a specific file
python classify_8k.py data/320193/2024/2024-02-01_None_8k.html

# Use different prompt strategies
python classify_8k.py tests/fixtures/sample_8k.html --strategy basic
python classify_8k.py tests/fixtures/sample_8k.html --strategy cot
python classify_8k.py tests/fixtures/sample_8k.html --strategy few_shot

# Enable verbose logging
python classify_8k.py tests/fixtures/sample_8k.html --verbose
```

### 3. List Available Files
See what 8-K files are available for classification:

```bash
python classify_8k.py --list-files
```

## Prompt Strategies

- **`basic`** - Simple classification prompts
- **`detailed`** - Rich prompts with event descriptions and keywords (default)
- **`cot`** - Chain-of-thought reasoning prompts  
- **`few_shot`** - Example-based learning prompts

## Pipeline Steps

1. **Text Extraction** - Clean text extraction from HTML using BeautifulSoup
2. **Event Classification** - LLM-based classification using configurable prompts
3. **Result Validation** - Parse and validate LLM responses
4. **Output** - Structured results with reasoning

## Expected Output

```
============================================================
8-K FILING CLASSIFICATION RESULTS
============================================================
File: tests/fixtures/sample_8k.html
Strategy: detailed
Text Length: 2,350 characters

CLASSIFICATION:
   Event Type: Financial Event
   Relevant: Yes
   Confidence: 85.0%

REASONING:
   This appears to be a quarterly earnings announcement...

RAW LLM RESPONSE:
   Event Type: Financial Event, Relevant: true
============================================================
```

## Configuration

The system uses these configuration files:

- **`config/llm_config.json`** - LLM settings (model, provider, options)
- **`config/event_config.json`** - Event types and relevance rules

## Requirements

- Python environment with required packages
- Ollama or other configured LLM provider
- Valid LLM model (e.g., `llama3.2:latest`, `qwen2.5-coder:14b`)

## Error Handling

The system includes robust error handling:
- Automatic retries for LLM failures
- Graceful degradation for parsing errors
- Comprehensive logging for debugging
- File validation and helpful error messages

Use `--verbose` flag for detailed troubleshooting information. 