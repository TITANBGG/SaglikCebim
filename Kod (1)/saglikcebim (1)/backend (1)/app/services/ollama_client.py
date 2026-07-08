"""
Doğrudan Ollama HTTP API istemcisi.
LangChain bağımlılığı olmadan /api/chat endpoint'ini kullanır.
Chat formatı (system + user rolleri) dil talimatlarını çok daha iyi tutar.
"""
import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional
from app.core.logging import get_logger

logger = get_logger("ollama_client")

_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


class OllamaClient:
    """
    Ollama /api/chat istemcisi.
    Mesajları system / user / assistant rolleriyle gönderir.
    """

    def __init__(self, base_url: str = _BASE_URL, model: str = _MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        format: Optional[str] = None,
        retries: int = 2,
    ) -> str:
        """
        system: Asistan kimliği ve kurallar
        user:   Hastanın bağlamı + mesajı
        format: "json" → Ollama'yı JSON modunda çalıştırır
        """
        payload: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2000,
            },
        }
        if format:
            payload["format"] = format

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        url = f"{self.base_url}/api/chat"

        last_exc: Exception = Exception("Bilinmeyen hata")
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    return result["message"]["content"]
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                last_exc = exc
                logger.warning(
                    "Ollama HTTP %s (deneme %d/%d): %s",
                    exc.code, attempt + 1, retries + 1, body[:200],
                )
                if attempt < retries and exc.code == 500:
                    time.sleep(2)
                    continue
                break
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "Ollama bağlantı hatası (deneme %d/%d): %s",
                    attempt + 1, retries + 1, exc,
                )
                if attempt < retries:
                    time.sleep(2)
                    continue
                break

        raise last_exc


# Uygulama genelinde paylaşılan tekil istemci
_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
