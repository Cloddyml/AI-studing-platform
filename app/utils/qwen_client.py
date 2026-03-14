import time

import httpx

from app.core.config import settings

_DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
_CHAT_ENDPOINT = f"{_DASHSCOPE_BASE_URL}/chat/completions"

# Таймаут на весь запрос к LLM
_TIMEOUT = httpx.Timeout(timeout=60.0)


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

        Raises:
            QwenAPIException: при любой ошибке на стороне API.
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

        t_start = time.monotonic()
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            try:
                response = await client.post(
                    _CHAT_ENDPOINT,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise QwenAPIException(
                    f"DashScope вернул HTTP {exc.response.status_code}: "
                    f"{exc.response.text}"
                ) from exc
            except httpx.RequestError as exc:
                raise QwenAPIException(
                    f"Сетевая ошибка при запросе к DashScope: {exc}"
                ) from exc

        elapsed_ms = int((time.monotonic() - t_start) * 1000)

        data = response.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise QwenAPIException(
                f"Неожиданная структура ответа DashScope: {data}"
            ) from exc

        return text, elapsed_ms


class QwenAPIException(Exception):
    """Ошибка при обращении к Qwen / DashScope."""
