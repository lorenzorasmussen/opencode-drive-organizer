"""
Ollama Integration for local LLM inference
"""

import os
import requests
import time
from typing import Dict, List, Optional, Generator, Any


class OllamaIntegration:
    """
    Integration with Ollama API for local LLM inference

    Features:
    - Text generation completion
    - Chat-style completion with message history
    - Streaming generation
    - Model listing and information
    - Custom parameters (temperature, max_tokens)
    - Timeout handling
    - Error handling for unavailability
    """

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        """
        Initialize Ollama integration

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def check_connection(self) -> bool:
        """
        Check if Ollama API is available

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> Optional[List[str]]:
        """
        List available models

        Returns:
            List of model names, or None if unavailable
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags", timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models

            return None
        except Exception:
            return None

    def generate(
        self,
        prompt: str,
        model: str = "llama2",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Optional[str]:
        """
        Generate text completion

        Args:
            prompt: Input prompt
            model: Model name (default: llama2)
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Returns:
            Generated text, or None if unavailable
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {"temperature": temperature},
            }

            if system_prompt:
                payload["system"] = system_prompt

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = self.session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                print(f"⚠️  Ollama API error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"⚠️  Ollama request timed out after {self.timeout}s")
            return None
        except Exception as e:
            print(f"⚠️  Error calling Ollama: {e}")
            return None

    def generate_stream(
        self,
        prompt: str,
        model: str = "llama2",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """
        Generate text completion with streaming

        Args:
            prompt: Input prompt
            model: Model name (default: llama2)
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)

        Yields:
            Text chunks as they're generated
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": temperature},
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout,
            )

            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    try:
                        import json

                        json_data = json.loads(data)
                        if "response" in json_data:
                            yield json_data["response"]
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            print(f"⚠️  Error in streaming generation: {e}")
            return

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2",
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Chat-style completion with message history

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: llama2)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated response, or None if unavailable
        """
        try:
            payload = {"model": model, "messages": messages, "stream": False}

            response = self.session.post(
                f"{self.base_url}/api/chat", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                print(f"⚠️  Ollama chat API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️  Error in chat completion: {e}")
            return None

    def get_model_info(self, model: str) -> Optional[Dict]:
        """
        Get information about a specific model

        Args:
            model: Model name

        Returns:
            Model information dict, or None if unavailable
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/show", json={"name": model}, timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"⚠️  Error getting model info: {e}")
            return None

    def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama library

        Args:
            model: Model name to pull

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True,
                timeout=None,
            )

            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    try:
                        import json

                        json_data = json.loads(data)
                        status = json_data.get("status", "")
                        if status:
                            print(f"  {status}")
                    except json.JSONDecodeError:
                        pass

            return True

        except Exception as e:
            print(f"⚠️  Error pulling model: {e}")
            return False

    def close(self):
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
