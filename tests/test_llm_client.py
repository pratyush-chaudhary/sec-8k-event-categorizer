#!/usr/bin/env python3
"""Test suite for LLM client."""

import sys
import os
import unittest
import json
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm import LLMClient


class TestLLMClient(unittest.TestCase):
    """Test cases for LLMClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "provider": "ollama",
            "model": "llama3.2:latest",
            "options": {"timeout": 30},
        }

    def test_client_with_direct_config(self):
        """Test LLM client initialization with direct config."""
        print("\n--- Testing direct config initialization ---")

        client = LLMClient(config=self.test_config)

        self.assertIsNotNone(client)
        self.assertIsNotNone(client.provider)

        model_info = client.get_model_info()
        self.assertEqual(model_info["provider"], "ollama")
        self.assertEqual(model_info["model"], "llama3.2:latest")

        print(f"✓ Client initialized with {model_info['provider']} - {model_info['model']}")

    def test_client_with_config_file(self):
        """Test LLM client initialization with config file."""
        print("\n--- Testing config file initialization ---")

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.test_config, f)
            temp_config_path = f.name

        try:
            client = LLMClient(config_path=temp_config_path)

            self.assertIsNotNone(client)
            model_info = client.get_model_info()
            self.assertEqual(model_info["provider"], "ollama")

            print(
                f"✓ Client loaded from config file: {model_info['provider']} - {model_info['model']}"
            )

        finally:
            # Clean up temp file
            os.unlink(temp_config_path)

    def test_client_with_default_config(self):
        """Test LLM client initialization with default config."""
        print("\n--- Testing default config initialization ---")

        client = LLMClient()

        self.assertIsNotNone(client)
        model_info = client.get_model_info()
        self.assertEqual(model_info["provider"], "ollama")

        print(
            f"✓ Client initialized with defaults: {model_info['provider']} - {model_info['model']}"
        )

    def test_availability_check(self):
        """Test LLM availability checking."""
        print("\n--- Testing availability check ---")

        client = LLMClient(config=self.test_config)

        is_available = client.is_available()
        self.assertIsInstance(is_available, bool)

        if is_available:
            print("✓ LLM is available")
        else:
            print("✗ LLM is not available (Ollama might not be running)")

    def test_text_generation(self):
        """Test text generation functionality."""
        print("\n--- Testing text generation ---")

        client = LLMClient(config=self.test_config)

        if not client.is_available():
            self.skipTest("LLM not available - skipping generation test")

        # Simple arithmetic test
        prompt = "What is 5 + 3? Answer with just the number."

        try:
            response = client.generate(prompt)

            self.assertIsInstance(response, str)
            self.assertGreater(len(response.strip()), 0)

            print(f"✓ Generated response for '{prompt}': {response}")

            # Check if response contains expected answer
            self.assertIn("8", response)

        except Exception as e:
            self.fail(f"Text generation failed: {e}")

    def test_different_models(self):
        """Test with different available models."""
        print("\n--- Testing different models ---")

        # Test available models
        test_models = ["llama3.2:latest", "qwen2.5-coder:14b"]

        for model in test_models:
            with self.subTest(model=model):
                config = {"provider": "ollama", "model": model, "options": {"timeout": 30}}

                try:
                    client = LLMClient(config=config)
                    is_available = client.is_available()

                    print(f"  {model}: {'Available' if is_available else 'Not available'}")

                    if is_available:
                        # Quick test generation
                        response = client.generate("Hello! Respond with 'Hi there!'")
                        self.assertIsInstance(response, str)
                        self.assertGreater(len(response), 0)
                        print(f"    Response: {response[:50]}...")

                except Exception as e:
                    print(f"    Error with {model}: {e}")

    def test_invalid_provider(self):
        """Test error handling for invalid provider."""
        print("\n--- Testing invalid provider ---")

        invalid_config = {"provider": "invalid_provider", "model": "test-model"}

        with self.assertRaises(ValueError):
            LLMClient(config=invalid_config)

        print("✓ Correctly raises error for invalid provider")

    def test_nonexistent_config_file(self):
        """Test handling of non-existent config file."""
        print("\n--- Testing non-existent config file ---")

        # Should fall back to default config
        client = LLMClient(config_path="/nonexistent/path/config.json")

        self.assertIsNotNone(client)
        model_info = client.get_model_info()
        self.assertEqual(model_info["provider"], "ollama")

        print("✓ Falls back to default config for non-existent file")


def test_manual():
    """Manual test function for interactive testing."""
    print("=" * 60)
    print("MANUAL TEST: LLM Client")
    print("=" * 60)

    # Test 1: Basic functionality
    print("\n1. Basic LLM Client Test")
    print("-" * 30)

    try:
        client = LLMClient()
        model_info = client.get_model_info()
        print(f"✓ Model: {model_info['provider']} - {model_info['model']}")

        if client.is_available():
            print("✓ LLM is available")

            # Test simple generation
            response = client.generate("Say 'Hello World' in a friendly way.")
            print(f"✓ Response: {response}")

        else:
            print("✗ LLM not available")
            print("  Make sure Ollama is running:")
            print("  - brew install ollama (if not installed)")
            print("  - ollama serve (start service)")
            print("  - ollama pull llama3.2:latest (download model)")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Custom config
    print("\n2. Custom Configuration Test")
    print("-" * 35)

    try:
        config = {"provider": "ollama", "model": "qwen2.5-coder:14b", "options": {"timeout": 30}}

        client = LLMClient(config=config)
        print(f"✓ Custom config loaded: {config['model']}")

        if client.is_available():
            print("✓ Custom model available")

            # Test code-specific prompt
            code_prompt = "Write a simple Python function that adds two numbers."
            response = client.generate(code_prompt)
            print(f"✓ Code response: {response[:100]}...")

        else:
            print("✗ Custom model not available")

    except Exception as e:
        print(f"✗ Custom config error: {e}")

    # Test 3: Config file
    print("\n3. Config File Test")
    print("-" * 25)

    config_path = "config/llm_config.json"
    if os.path.exists(config_path):
        try:
            client = LLMClient(config_path=config_path)
            model_info = client.get_model_info()
            print(f"✓ Config file loaded: {config_path}")
            print(f"✓ Model: {model_info['provider']} - {model_info['model']}")

            if client.is_available():
                print("✓ Config file model available")
            else:
                print("✗ Config file model not available")

        except Exception as e:
            print(f"✗ Config file error: {e}")
    else:
        print(f"✗ Config file not found: {config_path}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run manual test for detailed output
    test_manual()

    print("\nRUNNING UNIT TESTS")
    print("=" * 60)

    # Run unit tests
    unittest.main(argv=[""], exit=False, verbosity=2)
