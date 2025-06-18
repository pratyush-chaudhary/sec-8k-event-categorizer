"""Ollama LLM provider."""

import subprocess
import json
import shutil
from typing import Dict, Any, Optional


class OllamaProvider:
    """Ollama LLM provider implementation."""
    
    def __init__(self, model: str = "llama3.2", **options):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model name to use
            **options: Additional Ollama options
        """
        self.model = model
        self.options = options
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If Ollama is not available or generation fails
        """
        if not self.is_available():
            raise RuntimeError("Ollama is not available")
        
        try:
            # Prepare command
            cmd = ["ollama", "run", self.model]
            
            # Run Ollama
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=kwargs.get('timeout', 60)
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Ollama error: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama request timed out")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available and the model is accessible."""
        
        # Check if ollama command is available
        if not shutil.which("ollama"):
            return False
        
        try:
            # Check if ollama is running
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return False
            
            # Check if our model is available
            return self.model in result.stdout
            
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def pull_model(self) -> bool:
        """
        Pull the model if it's not available.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["ollama", "pull", self.model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout for model download
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def list_models(self) -> list:
        """
        List available models.
        
        Returns:
            List of available model names
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            # Parse the output to extract model names
            lines = result.stdout.strip().split('\n')
            models = []
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            
            return models
            
        except (subprocess.TimeoutExpired, Exception):
            return [] 