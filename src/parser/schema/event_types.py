"""Event type definitions and schemas for 8-K classification."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class EventConfig:
    """Configuration for event types and their relevance criteria."""
    
    event_type: str
    relevant: bool
    description: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class ClassificationResult:
    """Result of event classification."""
    
    event_type: str
    relevant: bool
    confidence: float = 0.0
    reasoning: str = ""
    raw_response: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'event_type': self.event_type,
            'relevant': self.relevant,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'raw_response': self.raw_response
        }


# No hardcoded defaults - all configuration comes from config files


def load_event_config(config_dict: Dict[str, Any]) -> Dict[str, EventConfig]:
    """
    Load event configuration from dictionary.
    
    Args:
        config_dict: Dictionary with event configuration
        
    Returns:
        Dictionary of EventConfig objects
    """
    configs = {}
    
    for event_type, config in config_dict.items():
        configs[event_type] = EventConfig(
            event_type=event_type,
            relevant=config.get("relevant", False),
            description=config.get("description", ""),
            keywords=config.get("keywords", [])
        )
    
    return configs


def load_default_event_config(config_file_path: str = "config/event_config.json") -> Dict[str, EventConfig]:
    """
    Load event configuration from default config file.
    
    Args:
        config_file_path: Path to the configuration file
        
    Returns:
        Dictionary of EventConfig objects
    """
    import json
    import os
    
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Event configuration file not found: {config_file_path}")
    
    with open(config_file_path, 'r') as f:
        config_dict = json.load(f)
    
    return load_event_config(config_dict)


def validate_classification_result(result: str, valid_event_types: List[str]) -> Optional[ClassificationResult]:
    """
    Parse and validate LLM classification result.
    
    Args:
        result: Raw LLM response
        valid_event_types: List of valid event type names
        
    Returns:
        ClassificationResult if valid, None otherwise
    """
    import re
    
    # Try to parse the result
    # Expected format: "Event Type: [Category], Relevant: [true/false]"
    pattern = r"Event Type:\s*([^,]+),\s*Relevant:\s*(true|false)"
    match = re.search(pattern, result, re.IGNORECASE)
    
    if not match:
        # Try alternative formats
        patterns = [
            r"([^:]+):\s*(true|false|yes|no)",
            r"Type:\s*([^,]+),\s*Relevant:\s*(true|false)",
            r"Classification:\s*([^,]+),\s*Significant:\s*(true|false)"
        ]
        
        for alt_pattern in patterns:
            match = re.search(alt_pattern, result, re.IGNORECASE)
            if match:
                break
    
    if not match:
        return None
    
    event_type = match.group(1).strip()
    relevant_str = match.group(2).strip().lower()
    
    # Normalize event type
    event_type_clean = None
    for valid_type in valid_event_types:
        if event_type.lower() == valid_type.lower():
            event_type_clean = valid_type
            break
    
    if not event_type_clean:
        # Try partial matching
        for valid_type in valid_event_types:
            if valid_type.lower() in event_type.lower() or event_type.lower() in valid_type.lower():
                event_type_clean = valid_type
                break
    
    if not event_type_clean:
        return None
    
    # Parse relevance
    relevant = relevant_str in ['true', 'yes', '1']
    
    # Extract reasoning if present
    reasoning = ""
    reasoning_patterns = [
        r"reasoning:\s*(.+?)(?:\n|$)",
        r"because:\s*(.+?)(?:\n|$)",
        r"explanation:\s*(.+?)(?:\n|$)"
    ]
    
    for pattern in reasoning_patterns:
        reason_match = re.search(pattern, result, re.IGNORECASE | re.DOTALL)
        if reason_match:
            reasoning = reason_match.group(1).strip()
            break
    
    return ClassificationResult(
        event_type=event_type_clean,
        relevant=relevant,
        confidence=0.8,  # Default confidence
        reasoning=reasoning,
        raw_response=result
    ) 