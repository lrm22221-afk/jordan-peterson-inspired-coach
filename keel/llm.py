"""Minimal OpenAI-compatible chat client (stdlib only). Configure with env vars:
KEEL_API_KEY (or OPENAI_API_KEY), KEEL_BASE_URL (default https://api.openai.com/v1), KEEL_MODEL.
"""
import json
import os
import urllib.request


class LLMError(RuntimeError):
    pass


class OpenAICompatLLM:
    def __init__(self, api_key=None, base_url=None, model=None, timeout=60):
        self.api_key = api_key or os.environ.get("KEEL_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("KEEL_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.environ.get("KEEL_MODEL") or "gpt-4o-mini"
        self.timeout = timeout
        if not self.api_key:
            raise LLMError("No API key: set KEEL_API_KEY (or OPENAI_API_KEY), or run with --offline.")

    def chat(self, messages, temperature=0.6) -> str:
        body = json.dumps({"model": self.model, "messages": messages, "temperature": temperature}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.load(r)
        except Exception as e:  # network / HTTP errors
            raise LLMError(f"LLM request failed: {e}") from e
        return data["choices"][0]["message"]["content"].strip()


class OfflineLLM:
    """Deterministic stand-in for tests and --offline demos: echoes the active stance."""

    def __init__(self):
        self.last_messages = None

    def chat(self, messages, temperature=0.0) -> str:
        self.last_messages = messages
        ctx = messages[-2]["content"] if len(messages) >= 2 else ""
        stance = "NORMAL"
        for line in ctx.splitlines():
            if line.startswith("STANCE:"):
                stance = line.split(":", 1)[1].strip()
        return f"[offline:{stance}] What is the smallest step you will actually take this week?"
