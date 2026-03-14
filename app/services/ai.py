from app.exceptions.excs import (
    AIServiceException,
    TaskNotFoundException,
    TopicNotFoundException,
)
from app.schemas.ai_interactions import (
    AIInteractionAddDTO,
    AIResponseDTO,
    ExplainRequestDTO,
    HintRequestDTO,
    InteractionType,
)
from app.services.base import BaseService
from app.utils.qwen_client import QwenAPIException, QwenClient

# ── Системные промпты ─────────────────────────────────────────────────────────

_SYSTEM_HINT = """\
Ты — опытный преподаватель Python с фокусом на data science (NumPy, Pandas, \
Matplotlib, Seaborn, PyTorch). Твоя задача — дать студенту направляющую подсказку, \
не раскрывая готового решения. Отвечай кратко, по-русски, используй примеры кода \
только если это действительно необходимо для понимания."""

_SYSTEM_EXPLAIN = """\
Ты — опытный преподаватель Python, специализирующийся на data science. \
Студент изучает теоретический материал и задаёт уточняющий вопрос. \
Дай развёрнутое, но понятное объяснение. При необходимости приводи \
короткие примеры кода. Отвечай по-русски."""


class AIService(BaseService):
    # ── Hint ──────────────────────────────────────────────────────────────────

    async def get_hint(self, user_id: int, data: HintRequestDTO) -> AIResponseDTO:
        task = await self.db.tasks.get_published_by_id(data.task_id)
        if task is None:
            raise TaskNotFoundException

        user_prompt = (
            f"Задача: {task.title}\n\n"
            f"Условие:\n{task.description}\n\n"
            f"Текущий код студента:\n```python\n{data.user_code}\n```\n\n"
            "Дай подсказку — что стоит проверить или в каком направлении двигаться."
        )

        ai_text, elapsed_ms = await self._call_qwen(_SYSTEM_HINT, user_prompt)

        await self._log(
            user_id=user_id,
            interaction_type=InteractionType.HINT,
            task_id=data.task_id,
            topic_id=task.topic_id,
            user_message=data.user_code,
            ai_response=ai_text,
            response_time_ms=elapsed_ms,
        )

        return AIResponseDTO(response=ai_text, response_time_ms=elapsed_ms)

    async def explain_topic(
        self, user_id: int, data: ExplainRequestDTO
    ) -> AIResponseDTO:
        topic = await self.db.topics.get_published_by_id(data.topic_id)
        if topic is None:
            raise TopicNotFoundException

        # Передаём теорию темы в контекст, если она есть
        theory_block = f"Теория темы:\n{topic.content}\n\n" if topic.content else ""
        user_prompt = (
            f"Тема: {topic.title}\n\n{theory_block}Вопрос студента: {data.question}"
        )

        ai_text, elapsed_ms = await self._call_qwen(_SYSTEM_EXPLAIN, user_prompt)

        await self._log(
            user_id=user_id,
            interaction_type=InteractionType.EXPLAIN,
            task_id=None,
            topic_id=data.topic_id,
            user_message=data.question,
            ai_response=ai_text,
            response_time_ms=elapsed_ms,
        )

        return AIResponseDTO(response=ai_text, response_time_ms=elapsed_ms)

    @staticmethod
    async def _call_qwen(system: str, user: str) -> tuple[str, int]:
        try:
            return await QwenClient.chat(system_prompt=system, user_prompt=user)
        except QwenAPIException as exc:
            raise AIServiceException from exc

    async def _log(
        self,
        *,
        user_id: int,
        interaction_type: InteractionType,
        task_id: int | None,
        topic_id: int | None,
        user_message: str | None,
        ai_response: str | None,
        response_time_ms: int,
    ) -> None:
        dto = AIInteractionAddDTO(
            user_id=user_id,
            task_id=task_id,
            topic_id=topic_id,
            interaction_type=interaction_type.value,
            user_message=user_message,
            ai_response=ai_response,
            response_time_ms=response_time_ms,
        )
        await self.db.ai_interactions.add(dto)
        await self.db.commit()
