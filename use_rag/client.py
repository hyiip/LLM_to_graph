"""LLM client wrapper for API calls.

This module provides a wrapper for LLM API calls using litellm or openai.
"""

import os


# Provider detection patterns and their corresponding env vars
PROVIDER_CONFIG = {
    "openai": {
        "prefixes": ["gpt-", "o1-", "o3-"],
        "env_var": "OPENAI_API_KEY",
    },
    "anthropic": {
        "prefixes": ["claude-"],
        "env_var": "ANTHROPIC_API_KEY",
    },
    "gemini": {
        "prefixes": ["gemini/", "gemini-"],
        "env_var": "GEMINI_API_KEY",
    },
}


def detect_provider(model: str) -> str | None:
    """Detect the provider from the model name.

    Args:
        model: The model identifier.

    Returns:
        The provider name or None if not detected.
    """
    model_lower = model.lower()
    for provider, config in PROVIDER_CONFIG.items():
        for prefix in config["prefixes"]:
            if model_lower.startswith(prefix):
                return provider
    return None


def get_api_key_for_provider(provider: str | None) -> str | None:
    """Get the API key for a provider from environment variables.

    Args:
        provider: The provider name.

    Returns:
        The API key or None if not found.
    """
    if provider and provider in PROVIDER_CONFIG:
        env_var = PROVIDER_CONFIG[provider]["env_var"]
        return os.environ.get(env_var)

    # Fallback: check all provider env vars
    for config in PROVIDER_CONFIG.values():
        key = os.environ.get(config["env_var"])
        if key:
            return key
    return None


class LLMClient:
    """Wrapper for LLM API calls using litellm or openai.

    This client supports multiple LLM providers through litellm:
    - OpenAI: gpt-5.2 (uses OPENAI_API_KEY)
    - Anthropic: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-5 (uses ANTHROPIC_API_KEY)
    - Google: gemini/gemini-3-flash-preview, gemini/gemini-3-pro-preview (uses GEMINI_API_KEY)

    Attributes:
        model: The model identifier (e.g., "gpt-5.2", "claude-sonnet-4-5").
        api_key: The API key for authentication.
        provider: The detected provider name.
    """

    def __init__(
        self,
        model: str = "gpt-5.2",
        api_key: str | None = None,
    ):
        """Initialize the LLM client.

        Args:
            model: Model identifier. Defaults to "gpt-5.2".
                   Examples: "gpt-5.2", "claude-sonnet-4-5", "gemini/gemini-3-flash-preview"
            api_key: API key. If None, auto-detects from environment based on model.
        """
        self.model = model
        self.provider = detect_provider(model)
        self.api_key = api_key or get_api_key_for_provider(self.provider)

        if not self.api_key:
            env_var_hint = ""
            if self.provider and self.provider in PROVIDER_CONFIG:
                env_var_hint = f" Set {PROVIDER_CONFIG[self.provider]['env_var']} for {self.provider}."
            else:
                env_vars = [c["env_var"] for c in PROVIDER_CONFIG.values()]
                env_var_hint = f" Set one of: {', '.join(env_vars)}."

            raise ValueError(
                f"API key required for model '{model}'.{env_var_hint} "
                "Or pass api_key parameter directly."
            )

    def complete(self, prompt: str) -> str:
        """Send a prompt to the LLM and get a response.

        Args:
            prompt: The prompt to send.

        Returns:
            The LLM's response text.

        Raises:
            ImportError: If neither litellm nor openai is installed.
        """
        return self.chat([{"role": "user", "content": prompt}])

    def chat(self, messages: list[dict]) -> str:
        """Send a conversation to the LLM and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            The LLM's response text.

        Raises:
            ImportError: If neither litellm nor openai is installed.
        """
        try:
            import litellm

            response = litellm.completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
            )
            return response.choices[0].message.content

        except ImportError:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return response.choices[0].message.content

            except ImportError:
                raise ImportError(
                    "Either 'litellm' or 'openai' package is required. "
                    "Install with: pip install litellm  OR  pip install openai"
                )
