"""Prompt templates for LLM-based event classification."""

from typing import Dict, List, Any

from .prompt_templates import (
    BASIC_CLASSIFICATION_TEMPLATE,
    DETAILED_CLASSIFICATION_TEMPLATE,
    CHAIN_OF_THOUGHT_TEMPLATE,
    FEW_SHOT_TEMPLATE,
    VALIDATION_TEMPLATE,
    DEFAULT_FEW_SHOT_EXAMPLES,
)


class ClassificationPrompts:
    """Collection of prompt templates for event classification."""

    @staticmethod
    def basic_classification_prompt(text: str, event_types: List[str]) -> str:
        """
        Generate a basic classification prompt.

        Args:
            text: 8-K filing text to classify
            event_types: List of possible event types

        Returns:
            Formatted prompt string
        """
        return BASIC_CLASSIFICATION_TEMPLATE.format(
            text=text,
            event_types=", ".join(event_types)
        )

    @staticmethod
    def detailed_classification_prompt(text: str, event_configs: Dict[str, Any]) -> str:
        """
        Generate a detailed classification prompt with event descriptions.

        Args:
            text: 8-K filing text to classify
            event_configs: Dictionary of event configurations with descriptions

        Returns:
            Formatted prompt string
        """
        # Build event type descriptions
        event_descriptions = []

        for event_type, config in event_configs.items():
            description = config.get("description", "")
            keywords = config.get("keywords", [])

            desc_text = f"- {event_type}: {description}"
            if keywords:
                desc_text += f" (Keywords: {', '.join(keywords)})"
            event_descriptions.append(desc_text)

        return DETAILED_CLASSIFICATION_TEMPLATE.format(
            text=text,
            event_descriptions=chr(10).join(event_descriptions)
        )

    @staticmethod
    def chain_of_thought_prompt(text: str, event_types: List[str]) -> str:
        """
        Generate a chain-of-thought classification prompt.

        Args:
            text: 8-K filing text to classify
            event_types: List of possible event types

        Returns:
            Formatted prompt string
        """
        return CHAIN_OF_THOUGHT_TEMPLATE.format(
            text=text,
            event_types=", ".join(event_types)
        )

    @staticmethod
    def few_shot_prompt(
        text: str, event_types: List[str], examples: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a few-shot classification prompt with examples.

        Args:
            text: 8-K filing text to classify
            event_types: List of possible event types
            examples: List of example classifications

        Returns:
            Formatted prompt string
        """
        if examples is None:
            examples = DEFAULT_FEW_SHOT_EXAMPLES

        # Build examples section
        examples_text = []
        for i, example in enumerate(examples, 1):
            examples_text.append(f"Example {i}:")
            examples_text.append(f"Text: {example['text']}")
            examples_text.append("REASONING:")
            examples_text.append(example.get('reasoning', 'Analysis of the key factors and materiality.'))
            examples_text.append("CLASSIFICATION:")
            examples_text.append(f"{example['classification']}")
            examples_text.append("")

        return FEW_SHOT_TEMPLATE.format(
            event_types=", ".join(event_types),
            examples_text=chr(10).join(examples_text),
            text=text
        )

    @staticmethod
    def validation_prompt(text: str, classification: str, event_types: List[str]) -> str:
        """
        Generate a prompt to validate a classification result.

        Args:
            text: Original 8-K filing text
            classification: Proposed classification
            event_types: List of valid event types

        Returns:
            Validation prompt string
        """
        return VALIDATION_TEMPLATE.format(
            text=text,
            classification=classification,
            event_types=", ".join(event_types)
        )


# Convenience functions for common prompt types
def get_basic_prompt(text: str, event_types: List[str]) -> str:
    """Get a basic classification prompt."""
    return ClassificationPrompts.basic_classification_prompt(text, event_types)


def get_detailed_prompt(text: str, event_configs: Dict[str, Any]) -> str:
    """Get a detailed classification prompt with descriptions."""
    return ClassificationPrompts.detailed_classification_prompt(text, event_configs)


def get_cot_prompt(text: str, event_types: List[str]) -> str:
    """Get a chain-of-thought prompt."""
    return ClassificationPrompts.chain_of_thought_prompt(text, event_types)


def get_few_shot_prompt(
    text: str, event_types: List[str], examples: List[Dict[str, str]] = None
) -> str:
    """Get a few-shot prompt with examples."""
    return ClassificationPrompts.few_shot_prompt(text, event_types, examples)
