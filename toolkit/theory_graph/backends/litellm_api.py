"""LiteLLM backend — one wrapper for OpenAI / Anthropic / Google / Ollama / …"""
from __future__ import annotations

from .base import EncodeResult


class LiteLLMBackend:
    def complete(
        self,
        messages: list[dict],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout_s: int = 120,
    ) -> EncodeResult:
        try:
            import litellm
        except ImportError as e:
            raise SystemExit(
                "litellm is required for backend=api. "
                "pip install litellm  (or use encoding.backend: manual)"
            ) from e

        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout_s,
        )
        choice = resp.choices[0].message
        text = choice.content or ""
        usage = None
        if getattr(resp, "usage", None) is not None:
            u = resp.usage
            usage = {
                "prompt_tokens": getattr(u, "prompt_tokens", None),
                "completion_tokens": getattr(u, "completion_tokens", None),
                "total_tokens": getattr(u, "total_tokens", None),
            }
        provider = model.split("/", 1)[0] if "/" in model else "unknown"
        return EncodeResult(
            text=text,
            raw=text,
            model_id=model,
            provider=provider,
            usage=usage,
        )
