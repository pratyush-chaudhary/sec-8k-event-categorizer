"""Generic LLM client package.

Provides a simple LLMClient interface that can work with different LLM providers
based on configuration.
"""

from .client import LLMClient

__all__ = ['LLMClient'] 