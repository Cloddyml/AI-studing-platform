import asyncio
import time

import httpx

from app.core.config import settings

_DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
_CHAT_ENDPOINT = f"{_DASHSCOPE_BASE_URL}/chat/completions"

_TIMEOUT = httpx.Timeout(timeout=60.0)
_MAX_RETRIES = 2
_RETRY_DELAY_SEC = 1.0

_http_client: httpx.AsyncClient | None = None


async def init_http_client() -> None:
    global _http_client
    _http_client = httpx.AsyncClient(timeout=_TIMEOUT)


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def _get_client() -> httpx.AsyncClient:
    if _http_client is None:
        raise RuntimeError(
            "HTTP client не инициализирован. "
            "Убедитесь, что lifespan подключён в FastAPI-приложении."
        )
    return _http_client


class QwenClient:
    @staticmethod
    async def chat(
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 1024,
    ) -> tuple[str, int]:
        """
        Отправить запрос в Qwen и вернуть (текст_ответа, время_мс).

        При HTTP 5xx делает до _MAX_RETRIES повторных попыток с паузой.

        Raises:
            QwenAPIException: при любой ошибке на стороне API после всех попыток.
        """
        payload = {
            "model": settings.QWEN_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "extra_body": {"enable_thinking": False},
        }
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

        client = _get_client()
        last_exc: Exception | None = None

        t_start = time.monotonic()

        for attempt in range(1 + _MAX_RETRIES):
            try:
                response = await client.post(
                    _CHAT_ENDPOINT,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                break  # успех — выходим из цикла
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code >= 500 and attempt < _MAX_RETRIES:
                    # Временная ошибка DashScope — подождём и повторим
                    await asyncio.sleep(_RETRY_DELAY_SEC)
                    last_exc = exc
                    continue
                raise QwenAPIException(
                    f"DashScope вернул HTTP {exc.response.status_code}: "
                    f"{exc.response.text}"
                ) from exc
            except httpx.RequestError as exc:
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY_SEC)
                    last_exc = exc
                    continue
                raise QwenAPIException(
                    f"Сетевая ошибка при запросе к DashScope: {exc}"
                ) from exc
        else:
            # Цикл завершился без break — все попытки исчерпаны
            raise QwenAPIException(
                f"Все {_MAX_RETRIES + 1} попытки запроса к DashScope провалились"
            ) from last_exc

        elapsed_ms = int((time.monotonic() - t_start) * 1000)

        data = response.json()
        try:
            text_response = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise QwenAPIException(
                f"Неожиданная структура ответа DashScope: {data}"
            ) from exc

        return text_response, elapsed_ms


class QwenAPIException(Exception):
    """Ошибка при обращении к Qwen / DashScope."""
