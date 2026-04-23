"""
evaluate_only.py
================
Запускает ТОЛЬКО оценку метрик — без генерации нового кода.
Полезно если хочешь переоценить уже сгенерированные файлы.

Запуск:
    python evaluate_only.py
    python evaluate_only.py --query "оригинальный запрос"
"""

import argparse

import mlflow

from config import OUTPUT_DIR, DOCKER_DIR
from metrics import LLM_JUDGES

parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default="Создай погодное приложение")
args, _ = parser.parse_known_args()
query = args.query

# ── Сбор файлов ───────────────────────────────────────────────────────────────

generated_files = {}
if OUTPUT_DIR.exists():
    for file_path in sorted(OUTPUT_DIR.iterdir()):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                generated_files[file_path.name] = content
                print(f"  ✓ {file_path.name:20} | {len(content):6} символов")
            except Exception as e:
                print(f"  ❌ {file_path.name}: {e}")

if not generated_files:
    print("❌ Файлов не найдено в OUTPUT_DIR. Сначала запусти main.py")
    exit(1)

all_code = "\n\n".join(generated_files.values())
print(f"\n✓ Файлов: {len(generated_files)}, размер: {len(all_code):,} символов")

# ── Оценка ────────────────────────────────────────────────────────────────────

with mlflow.start_run(run_name="evaluate_only"):
    mlflow.log_param("mode", "evaluate_only")
    mlflow.log_param("files_count", len(generated_files))

    results = mlflow.genai.evaluate(
        data=[{
            "inputs": {"query": query},
            "outputs": {
                "response": all_code,
                "files": generated_files,
            }
        }],
        scorers=LLM_JUDGES
    )

    print("\n📊 РЕЗУЛЬТАТЫ:")
    if hasattr(results, "metrics") and results.metrics:
        for name, value in results.metrics.items():
            if isinstance(value, (int, float)) and 0 <= value <= 1:
                print(f"  {name:.<50} {value:.0%}")
