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

# Niet-streamende calls (verhaalvelden) blokkeren de UI achter een spinner;
# daarom korter en zonder retry, met de fallback als vangnet.
COMPLETE_TIMEOUT = 15
COMPLETE_RETRIES = 0


class LLMError(Exception):
    """Een LLM-call die niet kon worden uitgevoerd; de app valt dan terug op de originele tekst."""


def _berichten(system, messages):
    """Systeemprompt plus berichten, met alleen de velden die de API kent
    (UI-markeringen zoals `verborgen` gaan niet mee)."""
    return [{"role": "system", "content": system}] + [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]


def api_key():
    try:
        if "OPEN_ROUTER_API" in st.secrets:
            return st.secrets["OPEN_ROUTER_API"]
    except Exception:
        pass
    return os.environ.get("OPEN_ROUTER_API", "")


def available():
    return bool(api_key())


def _client(timeout=REQUEST_TIMEOUT, max_retries=MAX_RETRIES):
    key = api_key()
    if not key:
        raise LLMError("Geen API-key geconfigureerd (OPEN_ROUTER_API).")
    return OpenAI(
        base_url=BASE_URL,
        api_key=key,
        timeout=timeout,
        max_retries=max_retries,
    )


def complete(system, messages, max_tokens=600, json_mode=False):
    """Eén niet-streamende completion; geeft de volledige tekst terug.

    Met `json_mode=True` wordt om een JSON-object gevraagd. Raise LLMError bij
    elke fout of een leeg antwoord.
    """
    client = _client(timeout=COMPLETE_TIMEOUT, max_retries=COMPLETE_RETRIES)
    extra = {"response_format": {"type": "json_object"}} if json_mode else {}
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=_berichten(system, messages),
            max_tokens=max_tokens,
            extra_body=EXTRA_BODY,
            **extra,
        )
        tekst = response.choices[0].message.content if response.choices else None
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    if not tekst or not tekst.strip():
        raise LLMError("Leeg antwoord van het taalmodel.")
    return tekst


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
            messages=_berichten(system, messages),
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
