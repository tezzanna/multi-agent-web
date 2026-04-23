"""
main.py
=======
Точка входа. Запускает полный пайплайн:
  1. Мультиагентная система (supervisor)
  2. Сбор сгенерированных файлов
  3. Оценка через MLflow + 8 метрик

Запуск:
    python main.py
    python main.py --query "Создай todo-приложение"
"""

import argparse
import json

import mlflow
from IPython.display import HTML, display

from config import init_dirs, OUTPUT_DIR, DOCKER_DIR, run_cmd
from agents import supervisor
from metrics import LLM_JUDGES, timed_run

# ── Аргументы командной строки ────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="Мультиагентная система генерации веб-приложений")
parser.add_argument(
    "--query",
    type=str,
    default="Создай веб-приложение, которое показывает погоду в Москве на ближайшие 3 дня. Данные бери с openweathermap.org.",
    help="Задача для мультиагентной системы"
)
args, _ = parser.parse_known_args()
query = args.query


# ── Шаг 1: Инициализация директорий ──────────────────────────────────────────

init_dirs()


# ── Шаг 2: Запуск мультиагентной системы ─────────────────────────────────────

print("\nЗапуск мультиагентной системы (LangChain Subagents)...")
print("=" * 60)

result = timed_run(
    "supervisor",
    supervisor.invoke,
    {"messages": [{"role": "user", "content": query}]},
    config={"recursion_limit": 80}
)

print("\n" + "=" * 60)
print("\n✅ Supervisor завершил работу:")
print(result["messages"][-1].content)


# ── Шаг 3: Показ созданных файлов ─────────────────────────────────────────────

saved = list(OUTPUT_DIR.iterdir())
if saved:
    print("\n📁 Созданные файлы проекта:")
    for f in sorted(saved):
        if f.is_file():
            print(f"   • {f.name}")

saved_docker = list(DOCKER_DIR.iterdir())
if saved_docker:
    print("\n🐳 Docker-файлы:")
    for f in sorted(saved_docker):
        print(f"   • {f.name}")


# ── Шаг 4: Статус контейнера и URL ────────────────────────────────────────────

print("\n" + "=" * 60)
_, status, _ = run_cmd("docker-compose ps", cwd=DOCKER_DIR.resolve())
print(f"\n📊 Статус контейнеров:\n{status}")

_, port_out, _ = run_cmd("docker-compose port weather-app 80", cwd=DOCKER_DIR.resolve())
port = port_out.split(":")[-1] if ":" in port_out else "8080"
url = f"http://localhost:{port}"
print(f"\n🌐 Приложение доступно: {url}")


# ── Шаг 5: Сбор файлов для оценки ────────────────────────────────────────────

print("\n" + "=" * 100)
print("ПОДГОТОВКА ДАННЫХ ДЛЯ СУДЕЙ")
print("=" * 100)

generated_files = {}
if OUTPUT_DIR.exists():
    print(f"\n📂 Папка: {OUTPUT_DIR}")
    for file_path in sorted(OUTPUT_DIR.iterdir()):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                generated_files[file_path.name] = content
                print(f"  ✓ {file_path.name:20} | {len(content):6} символов")
            except Exception as e:
                print(f"  ❌ {file_path.name}: {e}")

all_code = "\n\n".join([
    f"{'=' * 60}\nFILE: {filename}\n{'=' * 60}\n{content}"
    for filename, content in generated_files.items()
])

print(f"\n✓ Всего файлов: {len(generated_files)}")
print(f"✓ Общий размер кода: {len(all_code):,} символов")

eval_data = [
    {
        "inputs": {
            "query": query,
            "files": list(generated_files.keys()),
        },
        "outputs": {
            "response": all_code,
            "files": generated_files,
        }
    }
]


# ── Шаг 6: Оценка через MLflow ────────────────────────────────────────────────

print("\n" + "=" * 100)
print("ЗАПУСК ОЦЕНКИ С ИСПОЛЬЗОВАНИЕМ LLM СУДЕЙ")
print("=" * 100)

with mlflow.start_run(run_name="llm_evaluation"):

    mlflow.log_param("evaluation_type", "llm_based")
    mlflow.log_param("files_count", len(generated_files))
    mlflow.log_param("total_code_size", len(all_code))
    mlflow.log_param("query", query[:200])

    try:
        results = mlflow.genai.evaluate(
            data=[
                {
                    "inputs": {"query": query},
                    "outputs": {
                        "response": "\n".join(generated_files.values()),
                        "files": generated_files,
                    }
                }
            ],
            scorers=LLM_JUDGES
        )

        print("\n✅ ОЦЕНКА УСПЕШНО ЗАВЕРШЕНА!")
        print("\n📊 РЕЗУЛЬТАТЫ:")

        if hasattr(results, "metrics") and results.metrics:
            for metric_name, value in results.metrics.items():
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    print(f"  {metric_name:.<50} {value:.0%}")
                else:
                    print(f"  {metric_name:.<50} {value}")

        if hasattr(results, "tables") and "eval_results_table" in results.tables:
            df = results.tables["eval_results_table"]
            print("\n📋 Детали по строкам:")
            for col in df.columns:
                if col not in ["inputs", "outputs"]:
                    value = df.iloc[0][col]
                    if isinstance(value, str) and ":" in value:
                        print(f"\n  {col}")
                        print(f"     {value}")
                    elif isinstance(value, (int, float)) and 0 <= value <= 1:
                        print(f"  {col:.<50} {value:.0%}")

        print("\n✅ Результаты сохранены в MLflow!")
        print("   https://mlflow.aicorex.tech")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
