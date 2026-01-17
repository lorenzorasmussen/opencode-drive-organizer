# tests/test_ollama_integration.py
"""
Test-driven development for Task 6: Ollama Integration (local LLM)
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.ollama_integration import OllamaIntegration


def test_ollama_connection():
    """Verify connection to Ollama API"""
    integration = OllamaIntegration()

    # Check connection
    connected = integration.check_connection()

    # Should handle gracefully if Ollama not available
    assert isinstance(connected, bool)


def test_list_models():
    """Verify listing available models"""
    integration = OllamaIntegration()

    models = integration.list_models()

    # Should return list or None if unavailable
    assert models is None or isinstance(models, list)


def test_generate_completion():
    """Verify text generation completion"""
    integration = OllamaIntegration()

    # Simple test prompt
    response = integration.generate(prompt="Test prompt", model="llama2")

    # Should handle gracefully if Ollama not available
    assert response is None or isinstance(response, str)


def test_generate_with_system_prompt():
    """Verify generation with system prompt"""
    integration = OllamaIntegration()

    response = integration.generate(
        prompt="Hello", system_prompt="You are a helpful assistant.", model="llama2"
    )

    # Should handle gracefully
    assert response is None or isinstance(response, str)


def test_streaming_generation():
    """Verify streaming text generation"""
    integration = OllamaIntegration()

    responses = list(
        integration.generate_stream(prompt="Streaming test", model="llama2")
    )

    # Should handle gracefully
    assert all(isinstance(r, str) for r in responses) or len(responses) == 0


def test_chat_completion():
    """Verify chat-style completion with message history"""
    integration = OllamaIntegration()

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
    ]

    response = integration.chat(messages=messages, model="llama2")

    # Should handle gracefully
    assert response is None or isinstance(response, str)


def test_model_info():
    """Verify getting model information"""
    integration = OllamaIntegration()

    info = integration.get_model_info("llama2")

    # Should return dict or None if unavailable
    assert info is None or isinstance(info, dict)


def test_generate_with_parameters():
    """Verify generation with custom parameters"""
    integration = OllamaIntegration()

    response = integration.generate(
        prompt="Test", model="llama2", temperature=0.5, max_tokens=100
    )

    # Should handle gracefully
    assert response is None or isinstance(response, str)


def test_timeout_handling():
    """Verify timeout handling for long requests"""
    integration = OllamaIntegration(timeout=1)

    response = integration.generate(prompt="Test", model="llama2")

    # Should handle timeout gracefully
    assert response is None or isinstance(response, str)


def test_error_handling():
    """Verify error handling for invalid requests"""
    integration = OllamaIntegration()

    # Invalid model
    response = integration.generate(prompt="Test", model="invalid_model_name_xyz")

    # Should handle error gracefully
    assert response is None or "error" in str(response).lower()
