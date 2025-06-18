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
{', '.join(event_types)}

Provide your answer as 'Event Type: [Category], Relevant: [true/false]'.

The event should be marked as 'Relevant: true' if it could significantly impact the company's stock price or business operations, and 'Relevant: false' if it's a minor administrative or routine matter.

Classification:"""
        
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
            description = config.get('description', '')
            keywords = config.get('keywords', [])
            
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

Provide your answer in this exact format:
Event Type: [Category], Relevant: [true/false]

Reasoning: [Brief explanation of your decision]

Classification:"""
        
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
{', '.join(event_types)}

Please follow these steps:

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

Step 4: Final classification
Provide your final answer as:
Event Type: [Category], Relevant: [true/false]

Analysis:"""
        
        return prompt
    
    @staticmethod
    def few_shot_prompt(text: str, event_types: List[str], examples: List[Dict[str, str]] = None) -> str:
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
                    "classification": "Event Type: Acquisition, Relevant: true"
                },
                {
                    "text": "The company announced quarterly earnings results...",
                    "classification": "Event Type: Financial Event, Relevant: true"
                },
                {
                    "text": "John Smith was appointed as new Chief Technology Officer...",
                    "classification": "Event Type: Personnel Change, Relevant: true"
                }
            ]
        
        # Build examples section
        examples_text = []
        for i, example in enumerate(examples, 1):
            examples_text.append(f"Example {i}:")
            examples_text.append(f"Text: {example['text']}")
            examples_text.append(f"Classification: {example['classification']}")
            examples_text.append("")
        
        prompt = f"""Classify 8-K filing events into these categories:
{', '.join(event_types)}

{chr(10).join(examples_text)}

Now classify this filing:
Text: {text}

Classification:"""
        
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

Valid Categories: {', '.join(event_types)}

Questions to consider:
1. Is the event type correct?
2. Is the relevance assessment appropriate?
3. Does the classification make logical sense?

Respond with:
- "VALID" if the classification is correct
- "INVALID: [reason]" if there are issues

Your assessment:"""
        
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


def get_few_shot_prompt(text: str, event_types: List[str], examples: List[Dict[str, str]] = None) -> str:
    """Get a few-shot prompt with examples."""
    return ClassificationPrompts.few_shot_prompt(text, event_types, examples) 