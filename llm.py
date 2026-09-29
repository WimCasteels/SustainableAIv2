"""LLM-clientlaag: één abstractie richting de provider (Mistral via OpenRouter).

De provider en het model zijn configuratie; een latere rechtstreekse koppeling
met La Plateforme of een lokaal model vraagt alleen andere instellingen.
"""

import os

import streamlit as st
from openai import OpenAI

BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("LLM_MODEL", "mistralai/mistral-medium-3-5")

# Provider-routing vastzetten op Mistral (La Plateforme) en datacollectie door
# tussenliggende providers uitsluiten (zie design document §6.3).
EXTRA_BODY = {
    "provider": {
        "order": ["mistral"],
        "allow_fallbacks": False,
        "data_collection": "deny",
    }
}

REQUEST_TIMEOUT = 30
MAX_RETRIES = 1


class LLMError(Exception):
    """Een LLM-call die niet kon worden uitgevoerd; de app valt dan terug op de originele tekst."""


def api_key():
    try:
        if "OPEN_ROUTER_API" in st.secrets:
            return st.secrets["OPEN_ROUTER_API"]
    except Exception:
        pass
    return os.environ.get("OPEN_ROUTER_API", "")


def available():
    return bool(api_key())


def _client():
    key = api_key()
    if not key:
        raise LLMError("Geen API-key geconfigureerd (OPEN_ROUTER_API).")
    return OpenAI(
        base_url=BASE_URL,
        api_key=key,
        timeout=REQUEST_TIMEOUT,
        max_retries=MAX_RETRIES,
    )


def stream(system, messages, max_tokens=1024):
    """Start een streaming completion en geef een token-generator terug.

    `messages` is een lijst van {"role", "content"}-dicts (zonder system).
    Raise LLMError als de call niet opgestart kan worden; fouten tijdens het
    streamen komen als exception uit de generator en vangt de aanroeper op.
    """
    client = _client()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system}] + messages,
            stream=True,
            max_tokens=max_tokens,
            extra_body=EXTRA_BODY,
        )
    except Exception as exc:
        raise LLMError(str(exc)) from exc

    def tokens():
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return tokens()
