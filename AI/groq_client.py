import os
import requests
import json
from typing import Dict, Any, Optional
from flask import current_app


class GroqClient:
    """Simple Groq API client with OpenAI compatibility"""

    def __init__(self):
        self.api_key = current_app.config.get('GROQ_API_KEY')
        self.model = current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.base_url = current_app.config.get('GROQ_BASE_URL', 'https://api.groq.com/openai/v1')

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

    def chat_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.3) -> str:
        """
        Send a chat completion request to Groq API
        Returns the generated text response
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            return data['choices'][0]['message']['content'].strip()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected Groq API response format: {str(e)}")