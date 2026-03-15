from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_studing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Таймзона
    timezone="UTC",
    enable_utc=True,
    # Подтверждение задачи ПОСЛЕ выполнения, а не при получении.
    # Если воркер упадёт в середине — задача вернётся в очередь.
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Максимум 1 повторная попытка при неожиданном падении воркера
    task_max_retries=1,
    # Результаты храним 1 час (поллинг хранится в БД, Redis только как backend)
    result_expires=3600,
)
