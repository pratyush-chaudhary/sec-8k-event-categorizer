"""Event classifier for 8-K filing classification using LLMs."""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from ..llm.client import LLMClient
from .schema.event_types import (
    EventConfig, 
    ClassificationResult, 
    load_default_event_config,
    load_event_config,
    validate_classification_result
)
from .prompts.classification_prompts import ClassificationPrompts


class PromptStrategy(Enum):
    """Available prompt strategies for classification."""
    BASIC = "basic"
    DETAILED = "detailed"
    CHAIN_OF_THOUGHT = "cot"
    FEW_SHOT = "few_shot"


class EventClassifier:
    """
    Classifier for 8-K filing events using LLMs.
    
    This class orchestrates the entire classification pipeline:
    1. Load event configuration
    2. Generate appropriate prompts
    3. Call LLM for classification
    4. Parse and validate results
    """
    
    def __init__(
        self, 
        llm_config_path: str = "config/llm_config.json",
        event_config_path: str = "config/event_config.json",
        event_config_dict: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the event classifier.
        
        Args:
            llm_config_path: Path to LLM configuration file
            event_config_path: Path to event configuration file  
            event_config_dict: Optional event config dict (overrides file)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client
        self.llm_client = LLMClient(config_file=llm_config_path)
        
        # Load event configuration
        if event_config_dict:
            self.event_configs = load_event_config(event_config_dict)
        else:
            self.event_configs = load_default_event_config(event_config_path)
        
        self.event_types = list(self.event_configs.keys())
        
        self.logger.info(f"Initialized EventClassifier with {len(self.event_types)} event types")
    
    def classify(
        self, 
        text: str, 
        strategy: PromptStrategy = PromptStrategy.DETAILED,
        examples: Optional[List[Dict[str, str]]] = None,
        max_retries: int = 2
    ) -> Optional[ClassificationResult]:
        """
        Classify an 8-K filing text.
        
        Args:
            text: The filing text to classify
            strategy: Prompt strategy to use
            examples: Custom examples for few-shot learning
            max_retries: Maximum number of retries on parsing failure
            
        Returns:
            ClassificationResult if successful, None if failed
        """
        if not text.strip():
            self.logger.warning("Empty text provided for classification")
            return None
        
        # Generate prompt based on strategy
        prompt = self._generate_prompt(text, strategy, examples)
        
        # Attempt classification with retries
        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                response = self.llm_client.generate(prompt)
                
                if not response:
                    self.logger.warning(f"Empty response from LLM (attempt {attempt + 1})")
                    continue
                
                # Parse and validate response
                result = validate_classification_result(response, self.event_types)
                
                if result:
                    # Add configuration info to result
                    event_config = self.event_configs.get(result.event_type)
                    if event_config:
                        result.relevant = event_config.relevant
                    
                    self.logger.info(f"Successfully classified as: {result.event_type} (relevant: {result.relevant})")
                    return result
                else:
                    self.logger.warning(f"Failed to parse LLM response (attempt {attempt + 1}): {response[:100]}...")
                    
            except Exception as e:
                self.logger.error(f"Error during classification (attempt {attempt + 1}): {e}")
        
        self.logger.error(f"Failed to classify after {max_retries + 1} attempts")
        return None
    
    def classify_batch(
        self, 
        texts: List[str], 
        strategy: PromptStrategy = PromptStrategy.DETAILED,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> List[Optional[ClassificationResult]]:
        """
        Classify multiple texts in batch.
        
        Args:
            texts: List of filing texts to classify
            strategy: Prompt strategy to use
            examples: Custom examples for few-shot learning
            
        Returns:
            List of ClassificationResults (None for failed classifications)
        """
        results = []
        
        for i, text in enumerate(texts):
            self.logger.info(f"Classifying text {i + 1}/{len(texts)}")
            result = self.classify(text, strategy, examples)
            results.append(result)
        
        success_count = sum(1 for r in results if r is not None)
        self.logger.info(f"Batch classification complete: {success_count}/{len(texts)} successful")
        
        return results
    
    def validate_classification(
        self, 
        text: str, 
        classification: str
    ) -> bool:
        """
        Validate a classification using LLM.
        
        Args:
            text: Original filing text
            classification: Proposed classification
            
        Returns:
            True if validation passes, False otherwise
        """
        validation_prompt = ClassificationPrompts.validation_prompt(
            text, classification, self.event_types
        )
        
        try:
            response = self.llm_client.generate(validation_prompt)
            if not response:
                return False
            response_upper = response.upper()
            # Check for explicit VALID at start or as separate word, but not INVALID
            return ("VALID" in response_upper and "INVALID" not in response_upper) or response_upper.strip().startswith("VALID")
        except Exception as e:
            self.logger.error(f"Error during validation: {e}")
            return False
    
    def get_event_info(self, event_type: str) -> Optional[EventConfig]:
        """
        Get configuration information for an event type.
        
        Args:
            event_type: The event type name
            
        Returns:
            EventConfig if found, None otherwise
        """
        return self.event_configs.get(event_type)
    
    def get_relevant_event_types(self) -> List[str]:
        """
        Get list of event types marked as relevant.
        
        Returns:
            List of relevant event type names
        """
        return [
            event_type for event_type, config in self.event_configs.items()
            if config.relevant
        ]
    
    def _generate_prompt(
        self, 
        text: str, 
        strategy: PromptStrategy,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate prompt based on strategy.
        
        Args:
            text: Filing text to classify
            strategy: Prompt strategy to use
            examples: Custom examples for few-shot
            
        Returns:
            Generated prompt string
        """
        if strategy == PromptStrategy.BASIC:
            return ClassificationPrompts.basic_classification_prompt(text, self.event_types)
        
        elif strategy == PromptStrategy.DETAILED:
            # Convert EventConfig objects to dictionaries for prompt generation
            config_dicts = {}
            for event_type, config in self.event_configs.items():
                config_dicts[event_type] = {
                    'relevant': config.relevant,
                    'description': config.description,
                    'keywords': config.keywords
                }
            return ClassificationPrompts.detailed_classification_prompt(text, config_dicts)
        
        elif strategy == PromptStrategy.CHAIN_OF_THOUGHT:
            return ClassificationPrompts.chain_of_thought_prompt(text, self.event_types)
        
        elif strategy == PromptStrategy.FEW_SHOT:
            return ClassificationPrompts.few_shot_prompt(text, self.event_types, examples)
        
        else:
            raise ValueError(f"Unknown prompt strategy: {strategy}")


# Convenience function for quick classification
def classify_text(
    text: str, 
    strategy: str = "detailed",
    llm_config_path: str = "config/llm_config.json",
    event_config_path: str = "config/event_config.json"
) -> Optional[ClassificationResult]:
    """
    Quick classification function for single texts.
    
    Args:
        text: Filing text to classify
        strategy: Prompt strategy ("basic", "detailed", "cot", "few_shot")
        llm_config_path: Path to LLM config
        event_config_path: Path to event config
        
    Returns:
        ClassificationResult if successful, None otherwise
    """
    try:
        strategy_enum = PromptStrategy(strategy)
    except ValueError:
        strategy_enum = PromptStrategy.DETAILED
    
    classifier = EventClassifier(llm_config_path, event_config_path)
    return classifier.classify(text, strategy_enum) 