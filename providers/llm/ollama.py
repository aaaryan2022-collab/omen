# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Ollama Local LLM Provider implementation.
"""

import json
import re
from typing import List, Dict, Any, Optional, Generator
import requests
from providers.llm.base import LLMProvider, LLMResponse, ToolCallRequest
from app.config import config
from app.logging_config import logger


class OllamaProvider(LLMProvider):
    """Client for local Ollama server API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or config.ollama_base_url).rstrip("/")
        self.model = model or config.ollama_model
        self.timeout = timeout or config.ollama_timeout

    def check_connection(self) -> bool:
        """Returns True if Ollama service is reachable and responding."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama connection check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """Queries Ollama for all installed/available models."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if res.status_code == 200:
                data = res.json()
                models = [m["name"] for m in data.get("models", [])]
                return models
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
        return []

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Executes a non-streaming chat completion."""
        url = f"{self.base_url}/api/chat"
        temp = temperature if temperature is not None else config.ollama_temperature

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
            },
        }

        if tools:
            payload["tools"] = tools

        try:
            res = requests.post(url, json=payload, timeout=self.timeout)
            if res.status_code != 200:
                error_msg = f"Ollama API returned status {res.status_code}: {res.text}"
                logger.error(error_msg)
                return LLMResponse(content=f"Error: {error_msg}", model=self.model)

            data = res.json()
            message = data.get("message", {})
            content = message.get("content", "")
            thought = message.get("thought")

            # Parse tool calls
            tool_calls: List[ToolCallRequest] = []
            if "tool_calls" in message and message["tool_calls"]:
                for tc in message["tool_calls"]:
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    args = fn.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    tool_calls.append(ToolCallRequest(name=name, arguments=args))

            # Fallback JSON parsing if no native tool calls but content contains tool block
            if not tool_calls:
                tool_calls = self._extract_json_tool_calls(content)

            return LLMResponse(
                content=content,
                thought=thought,
                tool_calls=tool_calls,
                raw_response=data,
                tokens_used=data.get("eval_count"),
                model=self.model,
            )

        except requests.exceptions.ConnectionError:
            msg = "Could not connect to Ollama. Please ensure Ollama is running (`ollama serve`)."
            logger.error(msg)
            return LLMResponse(content=msg, model=self.model)
        except Exception as e:
            msg = f"Error during Ollama chat: {str(e)}"
            logger.error(msg)
            return LLMResponse(content=msg, model=self.model)

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, LLMResponse]:
        """Streams token chunks from Ollama API, returning the aggregated LLMResponse."""
        url = f"{self.base_url}/api/chat"
        temp = temperature if temperature is not None else config.ollama_temperature

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temp,
            },
        }

        if tools:
            payload["tools"] = tools

        full_content = ""
        full_thought = ""
        native_tool_calls: List[ToolCallRequest] = []
        raw_final_data: Dict[str, Any] = {}

        try:
            with requests.post(url, json=payload, stream=True, timeout=self.timeout) as resp:
                if resp.status_code != 200:
                    err = f"Ollama returned HTTP {resp.status_code}: {resp.text}"
                    yield err
                    return LLMResponse(content=err, model=self.model)

                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk_json = json.loads(line.decode("utf-8"))
                        msg = chunk_json.get("message", {})
                        delta = msg.get("content", "")
                        thought_delta = msg.get("thought", "")

                        if delta:
                            full_content += delta
                            yield delta

                        if thought_delta:
                            full_thought += thought_delta

                        if "tool_calls" in msg and msg["tool_calls"]:
                            for tc in msg["tool_calls"]:
                                fn = tc.get("function", {})
                                name = fn.get("name", "")
                                args = fn.get("arguments", {})
                                if isinstance(args, str):
                                    try:
                                        args = json.loads(args)
                                    except Exception:
                                        args = {}
                                native_tool_calls.append(ToolCallRequest(name=name, arguments=args))

                        if chunk_json.get("done"):
                            raw_final_data = chunk_json
                    except Exception:
                        continue

            tool_calls = native_tool_calls
            if not tool_calls:
                tool_calls = self._extract_json_tool_calls(full_content)

            return LLMResponse(
                content=full_content,
                thought=full_thought or None,
                tool_calls=tool_calls,
                raw_response=raw_final_data,
                tokens_used=raw_final_data.get("eval_count"),
                model=self.model,
            )

        except requests.exceptions.ConnectionError:
            err = "Could not connect to Ollama. Please ensure Ollama is running."
            yield err
            return LLMResponse(content=err, model=self.model)
        except Exception as e:
            err = f"Error during streaming: {str(e)}"
            yield err
            return LLMResponse(content=err, model=self.model)

    def _extract_json_tool_calls(self, text: str) -> List[ToolCallRequest]:
        """Extracts tool calls if LLM responds with JSON markdown blocks or raw JSON."""
        tool_calls: List[ToolCallRequest] = []
        # Look for ```json ... ``` blocks
        json_matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        for match in json_matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict):
                    if "tool" in data and "arguments" in data:
                        tool_calls.append(ToolCallRequest(name=data["tool"], arguments=data.get("arguments", {})))
                    elif "name" in data and "arguments" in data:
                        tool_calls.append(ToolCallRequest(name=data["name"], arguments=data.get("arguments", {})))
                    elif "tools" in data and isinstance(data["tools"], list):
                        for item in data["tools"]:
                            if "tool" in item:
                                tool_calls.append(ToolCallRequest(name=item["tool"], arguments=item.get("arguments", {})))
            except Exception:
                continue

        # Look for bare JSON objects
        if not tool_calls and text.strip().startswith("{") and text.strip().endswith("}"):
            try:
                data = json.loads(text.strip())
                if isinstance(data, dict):
                    if "tool" in data:
                        tool_calls.append(ToolCallRequest(name=data["tool"], arguments=data.get("arguments", {})))
                    elif "tools" in data and isinstance(data["tools"], list):
                        for item in data["tools"]:
                            if "tool" in item:
                                tool_calls.append(ToolCallRequest(name=item["tool"], arguments=item.get("arguments", {})))
            except Exception:
                pass

        return tool_calls


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
