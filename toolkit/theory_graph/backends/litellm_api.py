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
        num_ctx: int | None = None,
    ) -> EncodeResult:
        try:
            import litellm
        except ImportError as e:
            raise SystemExit(
                "litellm is required for backend=api. "
                "pip install litellm  (or use encoding.backend: manual)"
            ) from e

        extra: dict = {}
        if num_ctx is not None and model.split("/", 1)[0] in ("ollama", "ollama_chat"):
            # Ollama's server-side default context window (often 2048-4096) is
            # smaller than our codebook + few-shot + transcript prompts, which
            # silently truncates the input and makes the model ignore frozen
            # upstream premises. Forward an explicit num_ctx to avoid this.
            extra["num_ctx"] = num_ctx

        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout_s,
            **extra,
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
