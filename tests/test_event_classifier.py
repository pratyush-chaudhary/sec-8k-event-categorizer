"""Tests for EventClassifier functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import os

from src.parser.event_classifier import (
    EventClassifier, 
    PromptStrategy, 
    classify_text
)
from src.parser.schema.event_types import ClassificationResult


class TestEventClassifier(unittest.TestCase):
    """Test EventClassifier functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = "Apple Inc. announced the acquisition of XYZ Corp for $1.2 billion."
        
        # Sample event configuration
        self.sample_event_config = {
            "Acquisition": {
                "relevant": True,
                "description": "Mergers and acquisitions",
                "keywords": ["acquisition", "merger"]
            },
            "Other": {
                "relevant": False,
                "description": "Other events",
                "keywords": []
            }
        }
        
        # Mock LLM responses
        self.valid_llm_response = "Event Type: Acquisition, Relevant: true"
        self.invalid_llm_response = "This is not a valid response format"
        
    def create_temp_config_files(self):
        """Create temporary configuration files for testing."""
        # Create temporary LLM config
        llm_config = {
            "provider": "ollama",
            "model": "test-model",
            "options": {"temperature": 0.1}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(llm_config, f)
            llm_config_path = f.name
        
        # Create temporary event config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_event_config, f)
            event_config_path = f.name
        
        return llm_config_path, event_config_path

    def tearDown(self):
        """Clean up any temporary files."""
        # Clean up is handled by individual tests
        pass

    @patch('src.parser.event_classifier.LLMClient')
    def test_classifier_initialization(self, mock_llm_client):
        """Test EventClassifier initialization."""
        # Setup mock
        mock_client_instance = Mock()
        mock_llm_client.return_value = mock_client_instance
        
        # Test with event config dict
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Verify initialization
        self.assertEqual(len(classifier.event_types), 2)
        self.assertIn("Acquisition", classifier.event_types)
        self.assertIn("Other", classifier.event_types)
        
        # Verify LLM client was initialized
        mock_llm_client.assert_called_once_with(config_file="dummy_llm.json")

    @patch('src.parser.event_classifier.LLMClient')
    def test_classify_success(self, mock_llm_client):
        """Test successful classification."""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.valid_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test classification
        result = classifier.classify(self.sample_text)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ClassificationResult)
        self.assertEqual(result.event_type, "Acquisition")
        self.assertTrue(result.relevant)
        
        # Verify LLM was called
        mock_client_instance.generate.assert_called_once()

    @patch('src.parser.event_classifier.LLMClient')
    def test_classify_invalid_response(self, mock_llm_client):
        """Test classification with invalid LLM response."""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.invalid_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test classification
        result = classifier.classify(self.sample_text)
        
        # Should return None for invalid response
        self.assertIsNone(result)
        
        # Should have tried multiple times (max_retries + 1)
        self.assertEqual(mock_client_instance.generate.call_count, 3)

    @patch('src.parser.event_classifier.LLMClient')
    def test_classify_empty_text(self, mock_llm_client):
        """Test classification with empty text."""
        # Setup mock
        mock_client_instance = Mock()
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test with empty text
        result = classifier.classify("")
        
        # Should return None and not call LLM
        self.assertIsNone(result)
        mock_client_instance.generate.assert_not_called()

    @patch('src.parser.event_classifier.LLMClient')
    def test_classify_with_different_strategies(self, mock_llm_client):
        """Test classification with different prompt strategies."""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.valid_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test all strategies
        strategies = [
            PromptStrategy.BASIC,
            PromptStrategy.DETAILED,
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.FEW_SHOT
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                result = classifier.classify(self.sample_text, strategy=strategy)
                self.assertIsNotNone(result)
                self.assertEqual(result.event_type, "Acquisition")

    @patch('src.parser.event_classifier.LLMClient')
    def test_classify_batch(self, mock_llm_client):
        """Test batch classification."""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = self.valid_llm_response
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test batch classification
        texts = [
            "Text 1: Acquisition announcement",
            "Text 2: Another acquisition",
            "Text 3: Third acquisition"
        ]
        
        results = classifier.classify_batch(texts)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r is not None for r in results))
        self.assertTrue(all(r.event_type == "Acquisition" for r in results))
        
        # Verify LLM was called for each text
        self.assertEqual(mock_client_instance.generate.call_count, 3)

    @patch('src.parser.event_classifier.LLMClient')
    def test_validate_classification(self, mock_llm_client):
        """Test classification validation."""
        # Setup mock for validation response
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = "VALID - this classification is correct"
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test validation
        is_valid = classifier.validate_classification(
            self.sample_text, 
            "Event Type: Acquisition, Relevant: true"
        )
        
        self.assertTrue(is_valid)
        mock_client_instance.generate.assert_called_once()

    @patch('src.parser.event_classifier.LLMClient')
    def test_validate_classification_invalid(self, mock_llm_client):
        """Test classification validation with invalid response."""
        # Setup mock for invalid validation response
        mock_client_instance = Mock()
        mock_client_instance.generate.return_value = "INVALID: wrong event type"
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test validation
        is_valid = classifier.validate_classification(
            self.sample_text, 
            "Event Type: Wrong Type, Relevant: true"
        )
        
        self.assertFalse(is_valid)

    @patch('src.parser.event_classifier.LLMClient')
    def test_get_event_info(self, mock_llm_client):
        """Test getting event configuration info."""
        # Setup mock
        mock_llm_client.return_value = Mock()
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test getting event info
        acquisition_info = classifier.get_event_info("Acquisition")
        self.assertIsNotNone(acquisition_info)
        self.assertEqual(acquisition_info.event_type, "Acquisition")
        self.assertTrue(acquisition_info.relevant)
        
        # Test non-existent event
        unknown_info = classifier.get_event_info("Unknown Event")
        self.assertIsNone(unknown_info)

    @patch('src.parser.event_classifier.LLMClient')
    def test_get_relevant_event_types(self, mock_llm_client):
        """Test getting relevant event types."""
        # Setup mock
        mock_llm_client.return_value = Mock()
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test getting relevant events
        relevant_types = classifier.get_relevant_event_types()
        
        self.assertEqual(len(relevant_types), 1)
        self.assertIn("Acquisition", relevant_types)
        self.assertNotIn("Other", relevant_types)

    @patch('src.parser.event_classifier.LLMClient')
    def test_generate_prompt_strategies(self, mock_llm_client):
        """Test prompt generation for different strategies."""
        # Setup mock
        mock_llm_client.return_value = Mock()
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test each strategy
        strategies = [
            PromptStrategy.BASIC,
            PromptStrategy.DETAILED,
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.FEW_SHOT
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                prompt = classifier._generate_prompt(self.sample_text, strategy)
                self.assertIsInstance(prompt, str)
                self.assertGreater(len(prompt), 50)
                self.assertIn(self.sample_text, prompt)

    @patch('src.parser.event_classifier.LLMClient')
    def test_generate_prompt_invalid_strategy(self, mock_llm_client):
        """Test prompt generation with invalid strategy."""
        # Setup mock
        mock_llm_client.return_value = Mock()
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test with invalid strategy (create a mock enum value)
        class InvalidStrategy:
            pass
        
        invalid_strategy = InvalidStrategy()
        
        with self.assertRaises(ValueError):
            classifier._generate_prompt(self.sample_text, invalid_strategy)

    @patch('src.parser.event_classifier.EventClassifier')
    def test_classify_text_convenience_function(self, mock_classifier_class):
        """Test the convenience classify_text function."""
        # Setup mock
        mock_classifier_instance = Mock()
        mock_result = ClassificationResult(
            event_type="Acquisition",
            relevant=True,
            confidence=0.9
        )
        mock_classifier_instance.classify.return_value = mock_result
        mock_classifier_class.return_value = mock_classifier_instance
        
        # Test convenience function
        result = classify_text(self.sample_text, strategy="detailed")
        
        # Verify result
        self.assertEqual(result, mock_result)
        
        # Verify classifier was created and called correctly
        mock_classifier_class.assert_called_once_with(
            "config/llm_config.json", 
            "config/event_config.json"
        )
        mock_classifier_instance.classify.assert_called_once()

    @patch('src.parser.event_classifier.EventClassifier')
    def test_classify_text_invalid_strategy(self, mock_classifier_class):
        """Test convenience function with invalid strategy."""
        # Setup mock
        mock_classifier_instance = Mock()
        mock_classifier_instance.classify.return_value = None
        mock_classifier_class.return_value = mock_classifier_instance
        
        # Test with invalid strategy - should default to DETAILED
        result = classify_text(self.sample_text, strategy="invalid_strategy")
        
        # Should still work (defaults to DETAILED)
        mock_classifier_instance.classify.assert_called_once()

    def test_prompt_strategy_enum(self):
        """Test PromptStrategy enum values."""
        self.assertEqual(PromptStrategy.BASIC.value, "basic")
        self.assertEqual(PromptStrategy.DETAILED.value, "detailed")
        self.assertEqual(PromptStrategy.CHAIN_OF_THOUGHT.value, "cot")
        self.assertEqual(PromptStrategy.FEW_SHOT.value, "few_shot")

    @patch('src.parser.event_classifier.LLMClient')
    def test_llm_error_handling(self, mock_llm_client):
        """Test error handling when LLM client fails."""
        # Setup mock to raise exception
        mock_client_instance = Mock()
        mock_client_instance.generate.side_effect = Exception("LLM connection error")
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test classification - should handle error gracefully
        result = classifier.classify(self.sample_text)
        
        # Should return None when LLM fails
        self.assertIsNone(result)
        
        # Should have retried max_retries + 1 times
        self.assertEqual(mock_client_instance.generate.call_count, 3)


if __name__ == '__main__':
    unittest.main() 