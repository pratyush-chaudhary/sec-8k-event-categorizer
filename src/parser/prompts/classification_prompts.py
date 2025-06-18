"""Prompt templates for LLM-based event classification."""

from typing import Dict, List, Any


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
        prompt = f"""Classify the following 8-K filing event:

{text}

Choose from these categories:
{", ".join(event_types)}

Please provide your response in this exact structure:

REASONING:
[Provide a clear explanation of your analysis, including:
- What specific event is being reported
- Key factors that led to your classification decision
- Why this event is or isn't relevant for investors]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

        return prompt

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
        event_types = []

        for event_type, config in event_configs.items():
            event_types.append(event_type)
            description = config.get("description", "")
            keywords = config.get("keywords", [])

            desc_text = f"- {event_type}: {description}"
            if keywords:
                desc_text += f" (Keywords: {', '.join(keywords)})"
            event_descriptions.append(desc_text)

        prompt = f"""You are an expert financial analyst. Classify the following 8-K filing event:

Filing Content:
{text}

Event Categories:
{chr(10).join(event_descriptions)}

Instructions:
1. Read the filing content carefully
2. Identify the main business event being reported
3. Choose the most appropriate category from the list above
4. Determine if this event is relevant/significant for investors

An event is RELEVANT if it could materially impact:
- Stock price
- Company's financial performance
- Business operations
- Competitive position
- Strategic direction

An event is NOT RELEVANT if it's:
- Routine administrative filing
- Minor operational change
- Scheduled/expected announcement
- Immaterial to business performance

Please provide your response in this exact structure:

REASONING:
[Provide a comprehensive analysis including:
- Summary of the key event being reported
- Analysis of which category best fits and why
- Assessment of materiality and investor impact
- Justification for relevance determination]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

        return prompt

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
        prompt = f"""Analyze this 8-K filing step by step:

Filing Content:
{text}

Available Categories:
{", ".join(event_types)}

Please provide your response in this exact structure:

REASONING:
Step 1: Identify the key facts
- What specific event is being reported?
- Who are the parties involved?
- What are the financial/business implications?

Step 2: Match to category
- Which category best fits this event?
- Why does it fit this category better than others?

Step 3: Assess significance
- Could this materially impact the company's business?
- Would investors consider this important?
- Is this routine or exceptional?

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your step-by-step analysis:"""

        return prompt

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
            examples = [
                {
                    "text": "Apple Inc. announced the acquisition of XYZ Corp for $1.2 billion...",
                    "reasoning": "This is a significant acquisition announcement involving a substantial financial transaction. The $1.2 billion value indicates material impact on Apple's financial position and business strategy.",
                    "classification": "Event Type: Acquisition, Relevant: true",
                },
                {
                    "text": "The company announced quarterly earnings results showing 15% revenue growth...",
                    "reasoning": "Quarterly earnings with significant growth are highly material to investors as they directly impact stock valuation and demonstrate business performance.",
                    "classification": "Event Type: Financial Event, Relevant: true",
                },
                {
                    "text": "John Smith was appointed as new Chief Technology Officer...",
                    "reasoning": "Executive appointments at the CTO level can signal strategic direction changes and are relevant for investor assessment of company leadership and technology strategy.",
                    "classification": "Event Type: Personnel Change, Relevant: true",
                },
            ]

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

        prompt = f"""Classify 8-K filing events into these categories:
{", ".join(event_types)}

Here are some examples of the expected format:

{chr(10).join(examples_text)}

Now classify this filing using the same structure:

Text: {text}

Please provide your response in this exact structure:

REASONING:
[Your detailed analysis here]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

        return prompt

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
        prompt = f"""Please validate this event classification:

Original Filing:
{text}

Proposed Classification: {classification}

Valid Categories: {", ".join(event_types)}

Please provide your response in this exact structure:

REASONING:
[Analyze the following questions:
1. Is the event type correct?
2. Is the relevance assessment appropriate?
3. Does the classification make logical sense?
4. Provide specific justification for your assessment]

VALIDATION:
Status: [VALID or INVALID]
Issues: [If INVALID, describe the specific problems]

Begin your validation analysis:"""

        return prompt


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
