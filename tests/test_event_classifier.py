"""Tests for EventClassifier functionality."""

import unittest
from unittest.mock import Mock, patch

from src.parser.event_classifier import (
    EventClassifier, 
    PromptStrategy
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
        mock_llm_client.assert_called_once_with(config_path="dummy_llm.json")

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
    def test_generate_prompt_strategies(self, mock_llm_client):
        """Test prompt generation for different strategies."""
        # Setup mock
        mock_client_instance = Mock()
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test each strategy generates different prompts
        strategies = [
            PromptStrategy.BASIC,
            PromptStrategy.DETAILED,
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.FEW_SHOT
        ]
        
        prompts = []
        for strategy in strategies:
            prompt = classifier._generate_prompt(self.sample_text, strategy)
            prompts.append(prompt)
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)
        
        # All prompts should be different
        self.assertEqual(len(set(prompts)), len(strategies))

    @patch('src.parser.event_classifier.LLMClient')
    def test_generate_prompt_invalid_strategy(self, mock_llm_client):
        """Test prompt generation with invalid strategy."""
        # Setup mock
        mock_client_instance = Mock()
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Create invalid strategy
        class InvalidStrategy:
            value = "invalid"
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            classifier._generate_prompt(self.sample_text, InvalidStrategy())

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
        mock_client_instance.generate.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_client_instance
        
        # Create classifier
        classifier = EventClassifier(
            llm_config_path="dummy_llm.json",
            event_config_dict=self.sample_event_config
        )
        
        # Test classification should handle exception gracefully
        result = classifier.classify(self.sample_text)
        
        # Should return None when LLM fails
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 