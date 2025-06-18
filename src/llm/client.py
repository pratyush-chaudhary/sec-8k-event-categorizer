"""Main LLM client that provides a unified interface."""

import json
import os
from typing import Dict, Any, Optional
from .providers.ollama import OllamaProvider


class LLMClient:
    """Simple LLM client that can use different providers based on configuration."""
    
    def __init__(self, config_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM client.
        
        Args:
            config_path: Path to configuration file
            config: Configuration dictionary (if not using file)
        """
        if config:
            self.config = config
        elif config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "provider": "ollama",
                "model": "llama3.2",
                "options": {}
            }
        
        self.provider = self._create_provider()
    
    def _create_provider(self):
        """Create the appropriate LLM provider based on config."""
        
        provider_name = self.config.get("provider", "ollama").lower()
        model = self.config.get("model", "llama3.2")
        options = self.config.get("options", {})
        
        if provider_name == "ollama":
            return OllamaProvider(model=model, **options)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the configured LLM.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        return self.provider.generate(prompt, **kwargs)
    
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        return self.provider.is_available()
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""
        return {
            "provider": self.config.get("provider", "unknown"),
            "model": self.config.get("model", "unknown")
        } 