# Integration Tests for classify_8k.py

This directory contains comprehensive integration tests for the `classify_8k.py` end-to-end pipeline.

## Test Overview

The integration test suite (`test_classify_8k_integration.py`) provides both mocked and real data testing:

### Real Data Integration Tests

- **`test_real_data_integration_board_appointment()`** - Tests with actual SEC filing URL
  - URL: https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm
  - Expected: Personnel Change event (board appointment)
  - Tests the complete pipeline with real network requests and LLM calls

### Mocked Integration Tests

- **`test_classify_8k_filing_success_mocked()`** - Basic successful classification with mocked LLM
- **`test_classify_8k_filing_different_strategies()`** - Tests all prompt strategies
- **`test_classify_8k_filing_file_not_found()`** - Error handling for missing files
- **`test_classify_8k_filing_llm_failure_mocked()`** - LLM failure handling
- **`test_classify_8k_filing_url_download_mocked()`** - URL download with mocked HTTP
- **`test_main_function_integration()`** - Command-line interface testing
- **`test_print_results_output_format()`** - Output formatting verification
- **`test_verbose_logging_output()`** - Verbose mode testing
- **`test_sample_fixture_contains_expected_content()`** - Test data validation

## Running the Tests

### Prerequisites

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest
```

### Run All Integration Tests

```bash
python -m pytest tests/test_classify_8k_integration.py -v
```

### Run Specific Tests

```bash
# Real data test only
python -m pytest tests/test_classify_8k_integration.py::TestClassify8KIntegration::test_real_data_integration_board_appointment -v -s

# Mocked tests only (faster)
python -m pytest tests/test_classify_8k_integration.py -k "mocked" -v
```

### Manual Testing

You can also test the script directly:

```bash
# Test with real SEC URL
python classify_8k.py "https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm" --strategy detailed

# Test with local fixture
python classify_8k.py tests/fixtures/sample_8k.html --strategy basic --verbose
```

## Test Features

### Real Data Validation
- Downloads actual SEC filing content
- Tests complete pipeline including HTTP requests
- Validates content extraction and classification
- Checks for expected keywords and event types

### Mock Data Testing
- Fast execution without network dependencies  
- Tests error conditions and edge cases
- Validates internal component integration
- Ensures robust error handling

### Output Verification
- Tests result structure and data types
- Validates logging output and verbosity
- Checks command-line interface behavior
- Verifies formatted output displays

## Expected Results

For the board appointment SEC filing, you should see:
- **Event Type**: Personnel Change
- **Relevant**: Yes 
- **Confidence**: ~80%
- **Keywords Found**: director, board, appointment, elect, member

## Notes

- Real data tests may be skipped if SEC.gov blocks requests
- Network timeouts are handled gracefully with skip messages  
- The LLM model (`llama3.2:latest`) should be available in Ollama
- Tests validate both successful and failure scenarios 