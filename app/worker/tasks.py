"""
Celery-задача выполнения кода студента.

Жизненный цикл submission:
  PENDING → RUNNING → ACCEPTED | WRONG_ANSWER | TIME_LIMIT | MEMORY_LIMIT
                               | RUNTIME_ERROR | INTERNAL_ERROR

После ACCEPTED:
  - upsert в solutions (финальное решение)
  - increment_solved в users_progresses (прогресс по теме)
"""

import asyncio
import logging

from celery import Task

from app.core.database import async_session_maker
from app.models.submissions import SubmissionStatus
from app.repositories.solutions import SolutionsRepository
from app.repositories.submissions import SubmissionsRepository
from app.repositories.task_tests import TaskTestsRepository
from app.repositories.tasks import TasksRepository
from app.repositories.users_progresses import UsersProgressesRepository
from app.schemas.solutions import SolutionAddDTO
from app.worker.celery_app import celery_app
from app.worker.sandbox import SandboxResult, run_code

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Запускает корутину из синхронного Celery-воркера."""
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(
    bind=True,
    name="execute_submission",
    max_retries=1,
    default_retry_delay=5,
)
def execute_submission(self: Task, submission_id: int) -> None:
    """
    Точка входа Celery-задачи.

    bind=True нужен для self.retry() при неожиданных ошибках.
    Все DB-операции — async, поэтому оборачиваем в asyncio.
    """
    try:
        _run_async(_execute(submission_id))
    except Exception as exc:
        logger.exception(
            "Неожиданная ошибка при выполнении submission %d", submission_id
        )
        # Одна автоматическая повторная попытка через 5 сек
        raise self.retry(exc=exc)


async def _execute(submission_id: int) -> None:
    """Асинхронная логика выполнения — работает с БД напрямую через репозитории."""
    async with async_session_maker() as session:
        submissions_repo = SubmissionsRepository(session)
        tasks_repo = TasksRepository(session)
        task_tests_repo = TaskTestsRepository(session)
        solutions_repo = SolutionsRepository(session)
        progresses_repo = UsersProgressesRepository(session)

        # 1. Получаем submission
        submission = await submissions_repo.get_by_id(submission_id)
        if submission is None:
            logger.error("Submission %d не найден в БД", submission_id)
            return

        # 2. Меняем статус → RUNNING
        await submissions_repo.update_status(submission_id, SubmissionStatus.RUNNING)
        await session.commit()

        # 3. Получаем задачу и тесты
        task = await tasks_repo.get_published_by_id(submission.task_id)
        if task is None:
            logger.error(
                "Task %d не найден для submission %d", submission.task_id, submission_id
            )
            await submissions_repo.update_status(
                submission_id, SubmissionStatus.INTERNAL_ERROR
            )
            await session.commit()
            return

        tests = await task_tests_repo.get_by_task(submission.task_id)

        # 4. Прогоняем тесты последовательно
        #    При первом падении останавливаемся и сохраняем stderr
        final_status = SubmissionStatus.ACCEPTED
        combined_stdout = ""
        combined_stderr = ""
        all_passed = True

        if not tests:
            # Задача без тестов — просто проверяем, что код выполняется без ошибок
            result: SandboxResult = run_code(
                code=submission.code,
                test_code="",
                time_limit_sec=task.time_limit_sec,
                memory_limit_mb=task.memory_limit_mb,
            )
            combined_stdout = result.stdout
            combined_stderr = result.stderr

            if result.timed_out:
                final_status = SubmissionStatus.TIME_LIMIT
                all_passed = False
            elif result.memory_exceeded:
                final_status = SubmissionStatus.MEMORY_LIMIT
                all_passed = False
            elif result.exit_code != 0:
                final_status = SubmissionStatus.RUNTIME_ERROR
                all_passed = False
        else:
            for test in tests:
                result = run_code(
                    code=submission.code,
                    test_code=test.test_code,
                    time_limit_sec=task.time_limit_sec,
                    memory_limit_mb=task.memory_limit_mb,
                )
                combined_stdout += result.stdout
                combined_stderr += result.stderr

                if result.timed_out:
                    final_status = SubmissionStatus.TIME_LIMIT
                    all_passed = False
                    break
                elif result.memory_exceeded:
                    final_status = SubmissionStatus.MEMORY_LIMIT
                    all_passed = False
                    break
                elif result.exit_code != 0:
                    # AssertionError или любой другой exception
                    final_status = SubmissionStatus.WRONG_ANSWER
                    all_passed = False
                    break

        # 5. Обновляем статус submission
        await submissions_repo.update_status(
            submission_id,
            final_status,
            stdout=combined_stdout[:10_000],
            stderr=combined_stderr[:10_000],
            is_tests_passed=all_passed,
        )

        # 6. Если все тесты пройдены → upsert solution + обновляем прогресс
        if all_passed:
            solution_dto = SolutionAddDTO(
                user_id=submission.user_id,
                task_id=submission.task_id,
                code=submission.code,
            )
            await solutions_repo.upsert_solution(solution_dto)
            await progresses_repo.increment_solved(
                user_id=submission.user_id,
                topic_id=task.topic_id,
            )

        await session.commit()

        logger.info(
            "Submission %d завершён со статусом %s",
            submission_id,
            final_status.value,
        )
