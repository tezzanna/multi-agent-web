"""
config/settings.py
==================
Единое место для всех настроек проекта:
- переменные окружения
- инициализация MLflow
- создание моделей
- настройка директорий
"""

import os
import re
import subprocess
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
import mlflow

# ── MLflow ────────────────────────────────────────────────────────────────────
os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME", "")
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD", "")

mlflow.set_tracking_uri("https://mlflow.aicorex.tech")
mlflow.set_registry_uri("https://mlflow.aicorex.tech")
mlflow.set_workspace("multi-agent-web-development")
mlflow.set_experiment("demo_00")
mlflow.langchain.autolog()

# ── Директории ────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "scripts/demo_00"))
DOCKER_DIR = OUTPUT_DIR / "docker"

def init_dirs():
    """Очистить и пересоздать рабочие директории."""
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.is_file():
                f.unlink()
        print(f"🗑️  Папка очищена: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if DOCKER_DIR.exists():
        for f in DOCKER_DIR.iterdir():
            if f.is_file():
                f.unlink()
        print(f"🗑️  Папка очищена: {DOCKER_DIR}")
    DOCKER_DIR.mkdir(parents=True, exist_ok=True)

# ── Основная модель (генерация кода) ──────────────────────────────────────────
model = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_HOST"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model="Qwen/Qwen3.5-27B",
    timeout=120,
    temperature=0.7,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)

# ── Судья-модель (оценка метрик) ──────────────────────────────────────────────
judge_model = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_HOST"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model="openai/gpt-oss-20b",
    temperature=0.7,
)

# ── Утилиты ───────────────────────────────────────────────────────────────────
def save_file(filename: str, content: str) -> str:
    """Сохранить файл в OUTPUT_DIR, очистив markdown-обёртки."""
    content = re.sub(r'^```[\w]*\n?', '', content.strip())
    content = re.sub(r'\n?```$', '', content.strip())
    filepath = OUTPUT_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"   💾 Сохранено: {filepath}")
    return str(filepath)

def save_file_docker(filename: str, content: str) -> str:
    """Сохранить файл в DOCKER_DIR, очистив markdown-обёртки."""
    content = re.sub(r'^```[\w]*\n?', '', content.strip())
    content = re.sub(r'\n?```$', '', content.strip())
    filepath = DOCKER_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"   💾 Сохранено: {filepath}")
    return str(filepath)

def run_cmd(cmd: str, cwd: Path = None) -> tuple[int, str, str]:
    """Выполнить shell-команду, вернуть (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def invoke_with_retry(messages, retries: int = 3, delay: int = 5) -> str:
    """Вызвать основную модель с повторными попытками при обрыве соединения."""
    for attempt in range(1, retries + 1):
        try:
            result = model.invoke(messages)
            return result.content
        except Exception as e:
            err_str = str(e)
            if attempt < retries and any(x in err_str for x in [
                "Connection error", "RemoteProtocolError",
                "Server disconnected", "APIConnectionError"
            ]):
                print(f"   ⚠️  Обрыв соединения (попытка {attempt}/{retries}), жду {delay}с...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Превышено число попыток подключения к API")
