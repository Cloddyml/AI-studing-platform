"""
Sandbox для выполнения кода студента.

Принцип безопасности (слои):
  1. subprocess — код запускается в отдельном процессе, а не в текущем интерпретаторе
  2. resource limits — RLIMIT_AS (память) + RLIMIT_CPU (CPU-время) на уровне ОС
  3. Таймаут через subprocess.run(timeout=...) — убивает процесс при превышении
  4. (Опционально) Docker-контейнер — если нужна полная изоляция ФС и сети

Текущая реализация: subprocess + resource limits (достаточно для диплома).
Для продакшена: каждый запуск — отдельный Docker-контейнер.
"""

import resource
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    memory_exceeded: bool


def _make_preexec(memory_limit_bytes: int, cpu_limit_sec: int):
    """
    Возвращает функцию-preexec_fn для subprocess.
    Вызывается в дочернем процессе ДО exec() — устанавливает resource limits.
    Работает только на Unix/Linux (WSL2 — ок).
    """

    def preexec():
        # Лимит виртуальной памяти
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
        # Лимит CPU-времени в секундах (SIGKILL при превышении hard limit)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit_sec, cpu_limit_sec + 1))
        # Запрет создания новых файлов (защита от записи на диск)
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        # Запрет форка новых процессов (защита от fork bombs)
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

    return preexec


def run_code(
    code: str,
    test_code: str,
    *,
    time_limit_sec: int = 10,
    memory_limit_mb: int = 128,
) -> SandboxResult:
    """
    Выполняет код студента + тестовый код в изолированном процессе.

    Шаги:
      1. Объединяем код студента и тест в один файл
      2. Записываем во временный файл
      3. Запускаем `python temp_file.py` с resource limits
      4. Возвращаем результат

    Args:
        code:             Код студента
        test_code:        Тестовый код (assert'ы или unittest)
        time_limit_sec:   Лимит времени из tasks.time_limit_sec
        memory_limit_mb:  Лимит памяти из tasks.memory_limit_mb

    Returns:
        SandboxResult с stdout, stderr, exit_code, флагами превышения лимитов
    """
    # Объединяем код студента + тест
    full_code = textwrap.dedent(code) + "\n\n" + textwrap.dedent(test_code)

    memory_limit_bytes = memory_limit_mb * 1024 * 1024

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(full_code)
        tmp_path = Path(tmp.name)

    try:
        result = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=time_limit_sec,
            preexec_fn=_make_preexec(memory_limit_bytes, time_limit_sec),
        )
        return SandboxResult(
            stdout=result.stdout[:10_000],  # обрезаем огромный вывод
            stderr=result.stderr[:10_000],
            exit_code=result.returncode,
            timed_out=False,
            memory_exceeded=False,
        )
    except subprocess.TimeoutExpired:
        return SandboxResult(
            stdout="",
            stderr="Превышен лимит времени выполнения.",
            exit_code=-1,
            timed_out=True,
            memory_exceeded=False,
        )
    except MemoryError:
        return SandboxResult(
            stdout="",
            stderr="Превышен лимит памяти.",
            exit_code=-1,
            timed_out=False,
            memory_exceeded=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
