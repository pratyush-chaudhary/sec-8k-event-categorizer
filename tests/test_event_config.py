"""Tests for event configuration loading and validation."""

import os
import json
import tempfile
import unittest
from src.parser.schema.event_types import (
    EventConfig, 
    ClassificationResult, 
    load_event_config, 
    load_default_event_config,
    validate_classification_result
)
from src.parser.prompts.classification_prompts import (
    ClassificationPrompts,
    get_basic_prompt,
    get_detailed_prompt,
    get_cot_prompt,
    get_few_shot_prompt
)


class TestEventConfig(unittest.TestCase):
    """Test event configuration loading and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.expected_event_types = {
            "Acquisition", "Customer Event", "Personnel Change", 
            "Financial Event", "Scheduling Event", "Other"
        }
        
        # Sample configuration for testing
        self.sample_config = {
            "Test Event": {
                "relevant": True,
                "description": "Test event description",
                "keywords": ["test", "sample"]
            },
            "Irrelevant Event": {
                "relevant": False,
                "description": "Not important event",
                "keywords": ["irrelevant"]
            }
        }

    def test_load_default_event_config(self):
        """Test loading the default event configuration from JSON file."""
        config = load_default_event_config()
        
        # Check that all expected event types are loaded
        self.assertEqual(len(config), 6)
        self.assertEqual(set(config.keys()), self.expected_event_types)
        
        # Check that each event type has proper EventConfig structure
        for event_type, event_config in config.items():
            self.assertIsInstance(event_config, EventConfig)
            self.assertEqual(event_config.event_type, event_type)
            self.assertIsInstance(event_config.relevant, bool)
            self.assertIsInstance(event_config.description, str)
            self.assertIsInstance(event_config.keywords, list)
            
        # Test specific event types
        acquisition = config["Acquisition"]
        self.assertTrue(acquisition.relevant)
        self.assertIn("acquisition", acquisition.keywords)
        self.assertIn("merger", acquisition.keywords)
        
        scheduling = config["Scheduling Event"]
        self.assertFalse(scheduling.relevant)
        self.assertIn("schedule", scheduling.keywords)

    def test_load_event_config_from_dict(self):
        """Test loading event configuration from a dictionary."""
        config = load_event_config(self.sample_config)
        
        self.assertEqual(len(config), 2)
        self.assertIn("Test Event", config)
        self.assertIn("Irrelevant Event", config)
        
        test_event = config["Test Event"]
        self.assertEqual(test_event.event_type, "Test Event")
        self.assertTrue(test_event.relevant)
        self.assertEqual(test_event.description, "Test event description")
        self.assertEqual(test_event.keywords, ["test", "sample"])
        
        irrelevant_event = config["Irrelevant Event"]
        self.assertFalse(irrelevant_event.relevant)

    def test_load_event_config_missing_file(self):
        """Test error handling when config file is missing."""
        with self.assertRaises(FileNotFoundError):
            load_default_event_config("nonexistent_config.json")

    def test_load_event_config_with_custom_file(self):
        """Test loading event configuration from a custom file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_config, f)
            temp_file_path = f.name
        
        try:
            config = load_default_event_config(temp_file_path)
            self.assertEqual(len(config), 2)
            self.assertIn("Test Event", config)
        finally:
            os.unlink(temp_file_path)

    def test_event_config_with_missing_fields(self):
        """Test event configuration with missing optional fields."""
        minimal_config = {
            "Minimal Event": {
                "relevant": True
                # Missing description and keywords
            }
        }
        
        config = load_event_config(minimal_config)
        minimal_event = config["Minimal Event"]
        
        self.assertEqual(minimal_event.description, "")
        self.assertEqual(minimal_event.keywords, [])

    def test_validate_classification_result_basic_format(self):
        """Test validation of classification results in basic format."""
        valid_types = list(self.expected_event_types)
        
        # Test valid result
        result_text = "Event Type: Acquisition, Relevant: true"
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.event_type, "Acquisition")
        self.assertTrue(parsed.relevant)
        self.assertEqual(parsed.raw_response, result_text)

    def test_validate_classification_result_alternative_formats(self):
        """Test validation of classification results in alternative formats."""
        valid_types = list(self.expected_event_types)
        
        # Test alternative format 1
        result1 = "Personnel Change: true"
        parsed1 = validate_classification_result(result1, valid_types)
        self.assertIsNotNone(parsed1)
        self.assertEqual(parsed1.event_type, "Personnel Change")
        self.assertTrue(parsed1.relevant)
        
        # Test alternative format 2
        result2 = "Type: Financial Event, Relevant: false"
        parsed2 = validate_classification_result(result2, valid_types)
        self.assertIsNotNone(parsed2)
        self.assertEqual(parsed2.event_type, "Financial Event")
        self.assertFalse(parsed2.relevant)
        
        # Test alternative format 3
        result3 = "Classification: Other, Significant: false"
        parsed3 = validate_classification_result(result3, valid_types)
        self.assertIsNotNone(parsed3)
        self.assertEqual(parsed3.event_type, "Other")
        self.assertFalse(parsed3.relevant)

    def test_validate_classification_result_case_insensitive(self):
        """Test case-insensitive validation of classification results."""
        valid_types = list(self.expected_event_types)
        
        # Test with different cases
        result_text = "Event Type: ACQUISITION, Relevant: TRUE"
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.event_type, "Acquisition")
        self.assertTrue(parsed.relevant)

    def test_validate_classification_result_partial_matching(self):
        """Test partial matching for event types."""
        valid_types = list(self.expected_event_types)
        
        # Test partial match
        result_text = "Event Type: Customer, Relevant: true"
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.event_type, "Customer Event")
        self.assertTrue(parsed.relevant)

    def test_validate_classification_result_with_reasoning(self):
        """Test validation with reasoning included."""
        valid_types = list(self.expected_event_types)
        
        result_text = """Event Type: Acquisition, Relevant: true
        Reasoning: This appears to be a major acquisition announcement which would significantly impact stock price."""
        
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.event_type, "Acquisition")
        self.assertTrue(parsed.relevant)
        self.assertIn("acquisition announcement", parsed.reasoning.lower())

    def test_validate_classification_result_invalid_format(self):
        """Test validation with invalid format returns None."""
        valid_types = list(self.expected_event_types)
        
        # Test completely invalid format
        result_text = "This is not a valid classification result"
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNone(parsed)

    def test_validate_classification_result_invalid_event_type(self):
        """Test validation with invalid event type returns None."""
        valid_types = list(self.expected_event_types)
        
        # Test with invalid event type
        result_text = "Event Type: Invalid Type, Relevant: true"
        parsed = validate_classification_result(result_text, valid_types)
        
        self.assertIsNone(parsed)

    def test_classification_result_to_dict(self):
        """Test ClassificationResult to_dict method."""
        result = ClassificationResult(
            event_type="Acquisition",
            relevant=True,
            confidence=0.9,
            reasoning="Clear acquisition language",
            raw_response="Event Type: Acquisition, Relevant: true"
        )
        
        result_dict = result.to_dict()
        
        expected_keys = {'event_type', 'relevant', 'confidence', 'reasoning', 'raw_response'}
        self.assertEqual(set(result_dict.keys()), expected_keys)
        self.assertEqual(result_dict['event_type'], "Acquisition")
        self.assertTrue(result_dict['relevant'])
        self.assertEqual(result_dict['confidence'], 0.9)

    def test_default_config_structure_integrity(self):
        """Test that the default config has proper structure and values."""
        config = load_default_event_config()
        
        # Check each event type has required fields
        for event_type, event_config in config.items():
            # All events should have descriptions
            self.assertTrue(len(event_config.description) > 0, 
                          f"{event_type} should have a description")
            
            # Keywords should be a list (can be empty for "Other")
            self.assertIsInstance(event_config.keywords, list)
            
            # Relevant events should have keywords (except "Other")
            if event_config.relevant and event_type != "Other":
                self.assertTrue(len(event_config.keywords) > 0,
                              f"{event_type} should have keywords if relevant")

    def test_config_file_json_validity(self):
        """Test that the config file is valid JSON and has expected structure."""
        with open("config/event_config.json", 'r') as f:
            config_data = json.load(f)
        
        # Should be a dictionary
        self.assertIsInstance(config_data, dict)
        
        # Each event should have the required structure
        for event_type, config in config_data.items():
            self.assertIn("relevant", config)
            self.assertIn("description", config)
            self.assertIn("keywords", config)
            
            self.assertIsInstance(config["relevant"], bool)
            self.assertIsInstance(config["description"], str)
            self.assertIsInstance(config["keywords"], list)


class TestClassificationPrompts(unittest.TestCase):
    """Test prompt generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = "Apple Inc. announced the acquisition of XYZ Corp for $1.2 billion in cash and stock."
        self.event_types = ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Other"]
        self.event_configs = {
            "Acquisition": {
                "relevant": True,
                "description": "Mergers, acquisitions, asset purchases",
                "keywords": ["acquisition", "merger", "purchase"]
            },
            "Financial Event": {
                "relevant": True,
                "description": "Earnings, dividends, financial results",
                "keywords": ["earnings", "revenue", "dividend"]
            }
        }

    def test_basic_classification_prompt(self):
        """Test basic classification prompt generation."""
        prompt = ClassificationPrompts.basic_classification_prompt(self.sample_text, self.event_types)
        
        # Check that prompt contains essential elements
        self.assertIn(self.sample_text, prompt)
        self.assertIn("Classify the following 8-K filing event", prompt)
        self.assertIn("Event Type:", prompt)
        self.assertIn("Relevant:", prompt)
        
        # Check that all event types are included
        for event_type in self.event_types:
            self.assertIn(event_type, prompt)
        
        # Check formatting instructions
        self.assertIn("true/false", prompt)
        self.assertIn("Classification:", prompt)

    def test_detailed_classification_prompt(self):
        """Test detailed classification prompt with descriptions."""
        prompt = ClassificationPrompts.detailed_classification_prompt(self.sample_text, self.event_configs)
        
        # Check basic elements
        self.assertIn(self.sample_text, prompt)
        self.assertIn("Filing Content:", prompt)
        self.assertIn("Event Categories:", prompt)
        
        # Check that event descriptions and keywords are included
        self.assertIn("Acquisition: Mergers, acquisitions, asset purchases", prompt)
        self.assertIn("acquisition, merger, purchase", prompt)
        self.assertIn("Financial Event: Earnings, dividends, financial results", prompt)
        
        # Check instructions are present
        self.assertIn("expert financial analyst", prompt)
        self.assertIn("RELEVANT if it could materially impact", prompt)
        self.assertIn("Stock price", prompt)
        self.assertIn("Reasoning:", prompt)

    def test_chain_of_thought_prompt(self):
        """Test chain-of-thought prompt generation."""
        prompt = ClassificationPrompts.chain_of_thought_prompt(self.sample_text, self.event_types)
        
        # Check basic elements
        self.assertIn(self.sample_text, prompt)
        self.assertIn("step by step", prompt)
        
        # Check that all steps are included
        self.assertIn("Step 1: Identify the key facts", prompt)
        self.assertIn("Step 2: Match to category", prompt)
        self.assertIn("Step 3: Assess significance", prompt)
        self.assertIn("Step 4: Final classification", prompt)
        
        # Check prompting questions
        self.assertIn("What specific event is being reported?", prompt)
        self.assertIn("Which category best fits", prompt)
        self.assertIn("materially impact", prompt)
        
        # Check event types are listed
        for event_type in self.event_types:
            self.assertIn(event_type, prompt)

    def test_few_shot_prompt_with_default_examples(self):
        """Test few-shot prompt with default examples."""
        prompt = ClassificationPrompts.few_shot_prompt(self.sample_text, self.event_types)
        
        # Check basic structure
        self.assertIn(self.sample_text, prompt)
        self.assertIn("Example 1:", prompt)
        self.assertIn("Example 2:", prompt)
        self.assertIn("Example 3:", prompt)
        
        # Check default examples are included
        self.assertIn("Apple Inc. announced the acquisition", prompt)
        self.assertIn("quarterly earnings results", prompt)
        self.assertIn("Chief Technology Officer", prompt)
        
        # Check event types
        for event_type in self.event_types:
            self.assertIn(event_type, prompt)
        
        # Check final classification section
        self.assertIn("Now classify this filing:", prompt)
        self.assertIn("Classification:", prompt)

    def test_few_shot_prompt_with_custom_examples(self):
        """Test few-shot prompt with custom examples."""
        custom_examples = [
            {
                "text": "The company signed a major partnership agreement with Microsoft.",
                "classification": "Event Type: Customer Event, Relevant: true"
            },
            {
                "text": "Board of directors scheduled the annual meeting for next month.",
                "classification": "Event Type: Scheduling Event, Relevant: false"
            }
        ]
        
        prompt = ClassificationPrompts.few_shot_prompt(
            self.sample_text, 
            self.event_types, 
            custom_examples
        )
        
        # Check custom examples are included
        self.assertIn("partnership agreement with Microsoft", prompt)
        self.assertIn("annual meeting for next month", prompt)
        self.assertIn("Customer Event", prompt)
        self.assertIn("Scheduling Event", prompt)
        
        # Should not contain default examples in the examples section
        # Note: Our sample text happens to contain "XYZ Corp" but that's in the "Now classify" section
        self.assertNotIn("quarterly earnings results", prompt)  # This is from default examples

    def test_validation_prompt(self):
        """Test validation prompt generation."""
        classification = "Event Type: Acquisition, Relevant: true"
        prompt = ClassificationPrompts.validation_prompt(
            self.sample_text, 
            classification, 
            self.event_types
        )
        
        # Check all elements are included
        self.assertIn(self.sample_text, prompt)
        self.assertIn(classification, prompt)
        self.assertIn("validate this event classification", prompt)
        
        # Check validation questions
        self.assertIn("Is the event type correct?", prompt)
        self.assertIn("Is the relevance assessment appropriate?", prompt)
        self.assertIn("Does the classification make logical sense?", prompt)
        
        # Check response format
        self.assertIn("VALID", prompt)
        self.assertIn("INVALID", prompt)
        
        # Check event types are listed
        for event_type in self.event_types:
            self.assertIn(event_type, prompt)

    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        # Test basic prompt function
        basic_prompt = get_basic_prompt(self.sample_text, self.event_types)
        expected_basic = ClassificationPrompts.basic_classification_prompt(self.sample_text, self.event_types)
        self.assertEqual(basic_prompt, expected_basic)
        
        # Test detailed prompt function
        detailed_prompt = get_detailed_prompt(self.sample_text, self.event_configs)
        expected_detailed = ClassificationPrompts.detailed_classification_prompt(self.sample_text, self.event_configs)
        self.assertEqual(detailed_prompt, expected_detailed)
        
        # Test chain-of-thought function
        cot_prompt = get_cot_prompt(self.sample_text, self.event_types)
        expected_cot = ClassificationPrompts.chain_of_thought_prompt(self.sample_text, self.event_types)
        self.assertEqual(cot_prompt, expected_cot)
        
        # Test few-shot function
        few_shot_prompt = get_few_shot_prompt(self.sample_text, self.event_types)
        expected_few_shot = ClassificationPrompts.few_shot_prompt(self.sample_text, self.event_types)
        self.assertEqual(few_shot_prompt, expected_few_shot)

    def test_prompt_length_and_structure(self):
        """Test that prompts have reasonable length and structure."""
        prompts = {
            "basic": ClassificationPrompts.basic_classification_prompt(self.sample_text, self.event_types),
            "detailed": ClassificationPrompts.detailed_classification_prompt(self.sample_text, self.event_configs),
            "cot": ClassificationPrompts.chain_of_thought_prompt(self.sample_text, self.event_types),
            "few_shot": ClassificationPrompts.few_shot_prompt(self.sample_text, self.event_types)
        }
        
        for prompt_type, prompt in prompts.items():
            # Each prompt should be substantial (not empty or too short)
            self.assertGreater(len(prompt), 100, f"{prompt_type} prompt too short")
            
            # Should contain the input text
            self.assertIn(self.sample_text, prompt)
            
            # Should not have obvious formatting issues
            self.assertNotIn("{{", prompt)  # No unresolved template variables
            self.assertNotIn("}}", prompt)
            
            # Should end with a clear instruction
            self.assertTrue(
                prompt.strip().endswith(":") or 
                "Classification" in prompt[-50:] or 
                "Analysis" in prompt[-50:],
                f"{prompt_type} prompt doesn't end with clear instruction"
            )

    def test_prompt_with_empty_inputs(self):
        """Test prompt generation with edge case inputs."""
        empty_text = ""
        empty_types = []
        
        # Basic prompt with empty text
        prompt = ClassificationPrompts.basic_classification_prompt(empty_text, self.event_types)
        self.assertIn("Classify the following 8-K filing event", prompt)
        
        # Basic prompt with empty event types
        prompt = ClassificationPrompts.basic_classification_prompt(self.sample_text, empty_types)
        self.assertIn(self.sample_text, prompt)
        
        # Detailed prompt with empty configs
        prompt = ClassificationPrompts.detailed_classification_prompt(self.sample_text, {})
        self.assertIn(self.sample_text, prompt)

    def test_prompt_special_characters_handling(self):
        """Test prompt generation handles special characters correctly."""
        special_text = 'Apple announced "Project X" with 50% ownership & $1M investment.'
        
        prompt = ClassificationPrompts.basic_classification_prompt(special_text, self.event_types)
        
        # Check that special characters are preserved
        self.assertIn('"Project X"', prompt)
        self.assertIn('50%', prompt)
        self.assertIn('$1M', prompt)
        self.assertIn('&', prompt)


if __name__ == '__main__':
    unittest.main() 