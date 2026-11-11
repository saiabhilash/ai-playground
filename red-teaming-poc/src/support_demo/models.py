import asyncio
import logging
import time
from typing import TypeVar

import requests
from pydantic import BaseModel

from support_demo.agent import PURPOSE, ToolRequest

Schema = TypeVar("Schema", bound=BaseModel)
OLLAMA_URL = "http://127.0.0.1:11434"


class LocalModel:
    """Schema-constrained, loopback-only Ollama client."""

    def __init__(self, model: str, timeout: int = 180):
        self.model_name = model
        self.timeout = timeout

    def get_model_name(self):
        return f"ollama/{self.model_name}"

    def generate(
        self,
        prompt: str,
        schema: type[Schema] | None = None,
        *,
        system: str | None = None,
        json_schema: dict | None = None,
    ) -> Schema | str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2048},
            "keep_alive": "5m",
        }
        if schema is not None:
            payload["format"] = schema.model_json_schema()
        elif json_schema is not None:
            payload["format"] = json_schema
        if system is not None:
            payload["system"] = system
        logging.info(
            "Local generation: %s / %s",
            self.model_name,
            schema.__name__ if schema is not None else "text",
        )
        started = time.monotonic()
        response = requests.post(
            f"{OLLAMA_URL}/api/generate", json=payload, timeout=self.timeout
        )
        response.raise_for_status()
        text = response.json()["response"]
        result = schema.model_validate_json(text) if schema is not None else text
        logging.info("Local generation completed in %.1fs", time.monotonic() - started)
        return result

    async def a_generate(
        self, prompt: str, schema: type[Schema] | None = None, **kwargs
    ) -> Schema | str:
        return await asyncio.to_thread(self.generate, prompt, schema, **kwargs)

    def chat(
        self, messages: list[dict[str, str]], *, json_schema: dict | None = None,
        json_output: bool = False,
    ) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2048},
            "keep_alive": "5m",
        }
        if json_schema is not None:
            payload["format"] = json_schema
        elif json_output:
            payload["format"] = "json"
        logging.info("Local PyRIT chat: %s", self.model_name)
        response = requests.post(
            f"{OLLAMA_URL}/api/chat", json=payload, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("message"), dict):
            raise ValueError("Ollama returned an invalid chat response envelope.")
        text = data["message"].get("content")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Ollama returned an empty or invalid chat response.")
        return text

    async def a_chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        return await asyncio.to_thread(self.chat, messages, **kwargs)

    def plan(self, prompt: str) -> ToolRequest:
        result = self.generate(
            f"{PURPOSE}\n"
            "Select one tool action. Use respond if you decline or need clarification. "
            "Never invent an order ID. Return JSON only, matching the supplied schema.\n"
            f"UNTRUSTED USER MESSAGE:\n{prompt}",
            schema=ToolRequest,
        )
        if not isinstance(result, ToolRequest):
            raise TypeError("The planner did not return a ToolRequest.")
        return result

    def check_available(self) -> None:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        response.raise_for_status()
        names = {item["name"] for item in response.json()["models"]}
        normalized = self.model_name if ":" in self.model_name else f"{self.model_name}:latest"
        if normalized not in names:
            raise ValueError(
                f"Ollama model {normalized!r} is not installed. "
                f"Run: ollama pull {normalized}"
            )
