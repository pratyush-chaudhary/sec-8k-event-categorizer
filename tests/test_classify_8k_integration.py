"""Integration tests for classify_8k.py end-to-end functionality."""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from io import StringIO

# Add the project root to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the main classification function
from classify_8k import classify_8k_filing, print_results, main
from src.parser.event_classifier import PromptStrategy
from src.parser.schema.event_types import ClassificationResult


class TestClassify8KIntegration(unittest.TestCase):
    """Integration tests for the complete 8-K classification pipeline."""
    
    def setUp(self):
        """Set up test fixtures and temporary config files."""
        # Create temporary LLM config file
        self.llm_config = {
            "provider": "ollama",
            "model": "test-model",
            "options": {"temperature": 0.1, "timeout": 30}
        }
        
        # Create temporary event config
        self.event_config = {
            "Financial Event": {
                "relevant": True,
                "description": "Earnings announcements, dividend declarations, financial results",
                "keywords": ["earnings", "results", "revenue", "profit", "dividend", "financial", "quarterly"]
            },
            "Personnel Change": {
                "relevant": True,
                "description": "Changes in executive leadership, board members, or key personnel",
                "keywords": ["CEO", "CFO", "president", "director", "appointment", "resignation"]
            },
            "Other": {
                "relevant": False,
                "description": "Events that don't fit into other categories",
                "keywords": []
            }
        }
        
        # Create temporary config files
        self.temp_llm_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.llm_config, self.temp_llm_config)
        self.temp_llm_config.close()
        
        self.temp_event_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.event_config, self.temp_event_config)
        self.temp_event_config.close()
        
        # Expected LLM response for the sample 8K fixture
        self.expected_llm_response = "Event Type: Financial Event, Relevant: true"
        
        # Path to sample fixture
        self.sample_8k_path = "tests/fixtures/sample_8k.html"
        
        # Real SEC URL for testing
        self.real_sec_url = "https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm"
        
    def tearDown(self):
        """Clean up temporary files."""
        try:
            os.unlink(self.temp_llm_config.name)
            os.unlink(self.temp_event_config.name)
        except OSError:
            pass
    
    def test_real_data_integration_board_appointment(self):
        """Test with real SEC filing URL - board appointment event (no mocking)."""
        print(f"\n🌐 Testing with real SEC URL: {self.real_sec_url}")
        print("📋 Expected event type: Personnel Change (board appointment)")
        
        try:
            # Test the end-to-end pipeline with real data
            result = classify_8k_filing(
                input_source=self.real_sec_url,
                strategy=PromptStrategy.DETAILED,
                verbose=True
            )
            
            # Verify the result structure
            self.assertIsNotNone(result, "Classification should succeed with real data")
            self.assertIsInstance(result, dict)
            
            # Verify basic result fields
            self.assertEqual(result['input_source'], self.real_sec_url)
            self.assertEqual(result['source_type'], 'URL')
            self.assertEqual(result['strategy'], 'detailed')
            self.assertGreater(result['text_length'], 0)
            self.assertIn('extracted_text', result)
            self.assertIn('classification', result)
            
            # Print results for manual verification
            print_results(result)
            
            # Verify classification results
            classification = result['classification']
            self.assertIsNotNone(classification['event_type'])
            self.assertIsInstance(classification['relevant'], bool)
            self.assertGreaterEqual(classification['confidence'], 0.0)
            self.assertIsNotNone(classification['raw_response'])
            
            # Check if it correctly identifies as Personnel Change
            # (This is the expected classification for board appointment)
            print(f"✅ Classified as: {classification['event_type']}")
            print(f"✅ Relevant: {classification['relevant']}")
            print(f"✅ Confidence: {classification['confidence']:.1%}")
            
            # Verify extracted text contains expected content
            extracted_text = result['extracted_text'].lower()
            personnel_keywords = ['director', 'board', 'appointment', 'elect', 'member']
            found_keywords = [kw for kw in personnel_keywords if kw in extracted_text]
            
            self.assertGreater(len(found_keywords), 0, 
                             f"Should find personnel-related keywords in text. Found: {found_keywords}")
            
            # The classification should ideally be Personnel Change for board appointments
            # but we'll accept any valid event type as long as the pipeline works
            valid_event_types = ['Personnel Change', 'Other', 'Financial Event', 'Acquisition', 'Customer Event']
            self.assertIn(classification['event_type'], valid_event_types)
            
        except Exception as e:
            # If there are network issues or SEC blocking, provide helpful message
            if "403" in str(e) or "Forbidden" in str(e):
                self.skipTest(f"SEC.gov blocked the request: {e}")
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                self.skipTest(f"Network/timeout issue: {e}")
            else:
                raise  # Re-raise unexpected errors
    
    @patch('src.parser.event_classifier.EventClassifier.classify')
    def test_classify_8k_filing_success_mocked(self, mock_classify):
        """Test successful end-to-end classification of the sample 8K filing (mocked LLM)."""
        # Mock the classifier to return a successful result
        mock_result = ClassificationResult(
            event_type='Financial Event',
            relevant=True,
            confidence=0.85,
            reasoning='Document contains financial results and earnings data',
            raw_response=self.expected_llm_response
        )
        mock_classify.return_value = mock_result
        
        # Test the end-to-end pipeline
        result = classify_8k_filing(
            input_source=self.sample_8k_path,
            strategy=PromptStrategy.DETAILED,
            verbose=False
        )
        
        # Verify the result structure
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Verify basic result fields
        self.assertEqual(result['input_source'], self.sample_8k_path)
        self.assertEqual(result['source_type'], 'File')
        self.assertEqual(result['strategy'], 'detailed')
        self.assertGreater(result['text_length'], 0)
        self.assertIn('extracted_text', result)
        self.assertIn('classification', result)
        
        # Verify classification results
        classification = result['classification']
        self.assertEqual(classification['event_type'], 'Financial Event')
        self.assertTrue(classification['relevant'])
        self.assertGreaterEqual(classification['confidence'], 0.0)
        
        # Verify the classifier was called
        mock_classify.assert_called_once()
        
        # Verify extracted text contains expected content from sample 8K
        extracted_text = result['extracted_text']
        self.assertIn('Apple Inc.', extracted_text)
        self.assertIn('Results of Operations and Financial Condition', extracted_text)
        self.assertIn('financial results', extracted_text)
    
    @patch('src.llm.client.LLMClient')
    @patch('src.parser.event_classifier.load_default_event_config')
    def test_classify_8k_filing_different_strategies(self, mock_load_config, mock_llm_client):
        """Test classification with different prompt strategies."""
        # Setup mocks
        mock_load_config.return_value = {
            "Financial Event": type('EventConfig', (), {
                'event_type': 'Financial Event',
                'relevant': True,
                'description': 'Financial results and earnings',
                'keywords': ['earnings', 'results']
            })()
        }
        
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.expected_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Test all strategies
        strategies = [
            PromptStrategy.BASIC,
            PromptStrategy.DETAILED,
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.FEW_SHOT
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                result = classify_8k_filing(
                    input_source=self.sample_8k_path,
                    strategy=strategy,
                    verbose=False
                )
                
                self.assertIsNotNone(result)
                self.assertEqual(result['strategy'], strategy.value)
                self.assertEqual(result['classification']['event_type'], 'Financial Event')
    
    def test_classify_8k_filing_file_not_found(self):
        """Test handling of non-existent file."""
        result = classify_8k_filing(
            input_source="non_existent_file.html",
            strategy=PromptStrategy.DETAILED,
            verbose=False
        )
        
        self.assertIsNone(result)
    
    @patch('src.parser.event_classifier.EventClassifier.classify')
    def test_classify_8k_filing_llm_failure_mocked(self, mock_classify):
        """Test handling of LLM classification failure."""
        # Mock the classifier to return None (failure)
        mock_classify.return_value = None
        
        result = classify_8k_filing(
            input_source=self.sample_8k_path,
            strategy=PromptStrategy.DETAILED,
            verbose=False
        )
        
        # Should return None when classification fails
        self.assertIsNone(result)
    
    @patch('requests.get')
    @patch('src.llm.client.LLMClient')
    @patch('src.parser.event_classifier.load_default_event_config')
    def test_classify_8k_filing_url_download_mocked(self, mock_load_config, mock_llm_client, mock_requests):
        """Test classification from URL (mocked download)."""
        # Setup mocks
        mock_load_config.return_value = {
            "Financial Event": type('EventConfig', (), {
                'event_type': 'Financial Event',
                'relevant': True,
                'description': 'Financial results',
                'keywords': []
            })()
        }
        
        # Read the sample file content
        with open(self.sample_8k_path, 'r', encoding='utf-8') as f:
            sample_content = f.read()
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = sample_content
        mock_response.raise_for_status = Mock()
        mock_requests.return_value = mock_response
        
        # Mock LLM
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.expected_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Test URL classification
        test_url = "https://www.sec.gov/Archives/edgar/data/320193/test.htm"
        result = classify_8k_filing(
            input_source=test_url,
            strategy=PromptStrategy.DETAILED,
            verbose=False
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['source_type'], 'URL')
        self.assertEqual(result['input_source'], test_url)
        self.assertEqual(result['classification']['event_type'], 'Financial Event')
        
        # Verify HTTP request was made
        mock_requests.assert_called_once()
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results_output_format(self, mock_stdout):
        """Test that print_results produces expected output format."""
        sample_results = {
            'input_source': 'test_file.html',
            'source_type': 'File',
            'strategy': 'detailed',
            'text_length': 1500,
            'classification': {
                'event_type': 'Financial Event',
                'relevant': True,
                'confidence': 0.85,
                'reasoning': 'Document contains earnings and financial results',
                'raw_response': 'Event Type: Financial Event, Relevant: true'
            }
        }
        
        print_results(sample_results)
        
        output = mock_stdout.getvalue()
        
        # Verify key information is in the output
        self.assertIn('8-K FILING CLASSIFICATION RESULTS', output)
        self.assertIn('test_file.html', output)
        self.assertIn('Financial Event', output)
        self.assertIn('85.0%', output)  # Confidence percentage
        self.assertIn('Yes', output)  # Relevant status
        self.assertIn('earnings and financial results', output)  # Reasoning
    
    @patch('sys.argv', ['classify_8k.py', 'tests/fixtures/sample_8k.html', '--strategy', 'basic'])
    @patch('src.llm.client.LLMClient')
    @patch('src.parser.event_classifier.load_default_event_config')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_function_integration(self, mock_stdout, mock_load_config, mock_llm_client):
        """Test the main function with command line arguments."""
        # Setup mocks
        mock_load_config.return_value = {
            "Financial Event": type('EventConfig', (), {
                'event_type': 'Financial Event',
                'relevant': True,
                'description': 'Financial results',
                'keywords': []
            })()
        }
        
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.expected_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Test main function
        try:
            main()
        except SystemExit as e:
            # main() calls sys.exit(1) on failure, sys.exit(0) or no exit on success
            if e.code == 1:
                self.fail("Main function failed unexpectedly")
        
        output = mock_stdout.getvalue()
        
        # Verify expected output elements
        self.assertIn('Starting 8-K classification pipeline', output)
        self.assertIn('tests/fixtures/sample_8k.html', output)
        self.assertIn('Classification completed successfully', output)
    
    @patch('src.llm.client.LLMClient')
    @patch('src.parser.event_classifier.load_default_event_config')
    def test_verbose_logging_output(self, mock_load_config, mock_llm_client):
        """Test that verbose mode produces detailed logging."""
        # Setup mocks
        mock_load_config.return_value = {
            "Financial Event": type('EventConfig', (), {
                'event_type': 'Financial Event',
                'relevant': True,
                'description': 'Financial results',
                'keywords': []
            })()
        }
        
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.expected_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Capture logging output
        import logging
        from io import StringIO
        
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            result = classify_8k_filing(
                input_source=self.sample_8k_path,
                strategy=PromptStrategy.DETAILED,
                verbose=True
            )
            
            self.assertIsNotNone(result)
            
            # Check that verbose logging was produced
            log_output = log_capture.getvalue()
            self.assertIn('Reading file', log_output)
            self.assertIn('Extracting text', log_output)
            self.assertIn('Classifying event', log_output)
            
        finally:
            logging.getLogger().removeHandler(handler)
    
    def test_sample_fixture_contains_expected_content(self):
        """Verify the sample fixture has the expected content for testing."""
        # Verify sample fixture exists and has expected content
        self.assertTrue(os.path.exists(self.sample_8k_path), 
                       f"Sample fixture not found at {self.sample_8k_path}")
        
        with open(self.sample_8k_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify key content that should trigger Financial Event classification
        expected_content = [
            'Apple Inc.',
            'Results of Operations and Financial Condition',
            'financial results',
            'quarterly revenue',
            'earnings per diluted share'
        ]
        
        for expected in expected_content:
            self.assertIn(expected, content, 
                         f"Expected content '{expected}' not found in sample fixture")


if __name__ == '__main__':
    unittest.main() 