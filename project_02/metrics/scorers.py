"""
metrics/scorers.py
==================
Все 8 метрик оценки мультиагентной системы.

Каждый скорер:
- декорирован @scorer для интеграции с MLflow
- пишет свой балл в SCORES_CACHE для агрегации в llm_overall_assessment
- возвращает Feedback(value=0..1, rationale="текст")
"""

import json
import subprocess
import time as _time
import re as _re

import mlflow
from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer
from langchain_openai import ChatOpenAI

from config import judge_model, model, OUTPUT_DIR, DOCKER_DIR, run_cmd

# ── Глобальные состояния ──────────────────────────────────────────────────────

SCORES_CACHE: dict = {}       # {metric_name: score} — заполняется скорерами, читается агрегатором
AGENT_TIMINGS: dict = {}      # {agent_name: elapsed_sec} — заполняется через timed_run()


def timed_run(agent_name: str, agent_fn, *args, **kwargs):
    """
    Обёртка для запуска агента с замером времени.
    Сохраняет elapsed в AGENT_TIMINGS.

    Пример:
        result = timed_run("planner", run_planner, task)
    """
    t0 = _time.time()
    result = agent_fn(*args, **kwargs)
    elapsed = _time.time() - t0
    AGENT_TIMINGS[agent_name] = round(elapsed, 2)
    print(f"   ⏱️  {agent_name}: {elapsed:.1f}с")
    return result


# ── 1. Expert Code Review ─────────────────────────────────────────────────────

@scorer
def expert_code_review(outputs) -> Feedback:
    """Читаемость, безопасность, производительность, best practices кода."""
    code = str(outputs)

    if not code or len(code) < 100:
        return Feedback(value=0.0, rationale="Code too short")

    try:
        prompt = f"""Ты опытный разработчик. Проанализируй этот веб-код:

{code[:2000]}

Оцени по шкале 0-10:
1. Читаемость кода
2. Безопасность
3. Производительность
4. Следование best practices

JSON: {{"readability": 8, "security": 7, "performance": 8, "best_practices": 7}}

ТОЛЬКО JSON!"""

        response = judge_model.invoke(prompt)
        response_text = response.content.strip()

        try:
            scores = json.loads(response_text)
            avg_score = (
                scores.get("readability", 0) +
                scores.get("security", 0) +
                scores.get("performance", 0) +
                scores.get("best_practices", 0)
            ) / 4 / 10

            SCORES_CACHE['expert_code_review'] = avg_score
            return Feedback(
                value=avg_score,
                rationale=f"Expert review: Read:{scores.get('readability')}/10, "
                         f"Sec:{scores.get('security')}/10, "
                         f"Perf:{scores.get('performance')}/10, "
                         f"BP:{scores.get('best_practices')}/10"
            )
        except json.JSONDecodeError:
            return Feedback(value=0.6, rationale=f"Model: {response_text[:100]}")

    except Exception as e:
        return Feedback(value=0.5, rationale=f"Error: {str(e)[:50]}")


# ── 2. Functionality Check ────────────────────────────────────────────────────

@scorer
def llm_functionality_check(inputs, outputs) -> Feedback:
    """Соответствие требованиям, наличие багов, работоспособность."""
    if not inputs or not outputs:
        return Feedback(value=0.5, rationale="No data")

    requirement = str(inputs)
    code = str(outputs)

    try:
        prompt = f"""Проверь соответствие кода требованиям.

ТРЕБОВАНИЕ: {requirement}

КОД: {code[:1500]}

Вопросы:
1. Реализует ли код основные требования? (да/нет)
2. Есть ли потенциальные баги? (да/нет)
3. Код будет работать как ожидается? (да/нет)

JSON: {{"meets_requirements": true, "has_bugs": false, "will_work": true, "confidence": 0.9}}

ТОЛЬКО JSON!"""

        response = judge_model.invoke(prompt)
        response_text = response.content.strip()

        try:
            result = json.loads(response_text)
            score = 0.0
            if result.get("meets_requirements"):
                score += 0.4
            if not result.get("has_bugs"):
                score += 0.3
            if result.get("will_work"):
                score += 0.3

            confidence = result.get("confidence", 0.0)
            final_score = score * confidence

            SCORES_CACHE['llm_functionality_check'] = final_score
            return Feedback(
                value=final_score,
                rationale=f"Функция: {'✓' if result.get('meets_requirements') else '✗'}, "
                         f"Баги: {'✗' if result.get('has_bugs') else '✓'}, "
                         f"Работает: {'✓' if result.get('will_work') else '✗'}"
            )
        except Exception:
            return Feedback(value=0.5, rationale=response_text[:80])

    except Exception as e:
        return Feedback(value=0.5, rationale=f"Error: {str(e)[:50]}")


# ── 3. Architecture Assessment ────────────────────────────────────────────────

@scorer
def llm_architecture_assessment(outputs) -> Feedback:
    """Модульность, масштабируемость, поддерживаемость, DRY."""
    code = str(outputs)

    if not code or len(code) < 200:
        return Feedback(value=0.3, rationale="Code too short for architecture assessment")

    try:
        prompt = f"""Ты архитектор. Оцени архитектуру этого кода:

{code[:2000]}

Оцени (1-10):
- Модульность (разделение на части)
- Масштабируемость (легко ли добавлять новое)
- Поддерживаемость (легко ли менять/исправлять)
- Повторное использование (DRY принцип)

JSON формат:
{{"modularity": 7, "scalability": 6, "maintainability": 8, "reusability": 7}}

ТОЛЬКО JSON!"""

        response = model.invoke(prompt)
        response_text = response.content.strip()

        try:
            scores = json.loads(response_text)
            avg = (
                scores.get("modularity", 5) +
                scores.get("scalability", 5) +
                scores.get("maintainability", 5) +
                scores.get("reusability", 5)
            ) / 4 / 10

            SCORES_CACHE['llm_architecture_assessment'] = avg
            return Feedback(
                value=avg,
                rationale=f"Architecture: Modularity {scores.get('modularity')}/10, "
                         f"Scalability {scores.get('scalability')}/10, "
                         f"Maintainability {scores.get('maintainability')}/10, "
                         f"Reusability {scores.get('reusability')}/10"
            )
        except json.JSONDecodeError:
            return Feedback(value=0.5, rationale=response_text[:100])

    except Exception as e:
        return Feedback(value=0.5, rationale=f"Error: {str(e)[:50]}")


# ── 4. Overall Assessment (агрегатор) ─────────────────────────────────────────

@scorer
def llm_overall_assessment(inputs, outputs) -> Feedback:
    """Взвешенный агрегат всех метрик + финальный verdict LLM."""
    WEIGHTS = {
        "expert_code_review":          0.20,
        "llm_functionality_check":     0.20,
        "llm_architecture_assessment": 0.15,
        "docker_build_assessment":     0.15,
        "webpage_quality_assessment":  0.15,
        "agent_timing_metric":         0.08,
        "test_results_metric":         0.07,
    }

    scores_used = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for metric, weight in WEIGHTS.items():
        if metric in SCORES_CACHE:
            scores_used[metric] = SCORES_CACHE[metric]
            weighted_sum += SCORES_CACHE[metric] * weight
            total_weight += weight

    # Fallback: кэш пуст — просим LLM дать оценку напрямую
    if not scores_used:
        code = str(outputs)[:2000] if outputs else "No code"
        requirement = str(inputs) if inputs else "No requirement"
        try:
            prompt = (
                "Ты senior разработчик. Оцени проект от 0 до 100.\n\n"
                f"ТРЕБОВАНИЕ:\n{requirement}\n\nКОД:\n{code}\n\n"
                'ТОЛЬКО JSON: {"overall_score": 75, "summary": "...", "main_issues": "..."}'
            )
            response = judge_model.invoke(prompt)
            result = json.loads(response.content.strip())
            score = result.get("overall_score", 50) / 100
            return Feedback(
                value=round(score, 3),
                rationale=(
                    f"[Fallback LLM] {result.get('summary', '')} | "
                    f"Issues: {result.get('main_issues', 'None')}"
                )
            )
        except Exception as e:
            return Feedback(value=0.5, rationale=f"Fallback error: {str(e)[:60]}")

    aggregate = weighted_sum / total_weight if total_weight > 0 else 0.0

    scores_str = "\n".join(f"  {k}: {v:.0%}" for k, v in scores_used.items())
    code_snippet = str(outputs)[:1000] if outputs else ""
    requirement = str(inputs)[:500] if inputs else "No requirement"

    try:
        prompt = (
            "Ты senior разработчик. Дай финальный вывод по проекту.\n\n"
            f"ТРЕБОВАНИЕ:\n{requirement}\n\n"
            f"БАЛЛЫ МЕТРИК:\n{scores_str}\n\n"
            f"ФРАГМЕНТ КОДА:\n{code_snippet}\n\n"
            "Учти все баллы выше и дай краткий синтез: что хорошо, что надо исправить в первую очередь.\n"
            'ТОЛЬКО JSON: {"summary": "...", "priority_fix": "...", "verdict": "production_ready|needs_work|critical_issues"}'
        )
        response = judge_model.invoke(prompt)
        result = json.loads(response.content.strip())
        rationale = (
            f"Aggregate {aggregate:.0%} (weighted) | "
            f"Verdict: {result.get('verdict', '?')} | "
            f"{result.get('summary', '')} | "
            f"Fix first: {result.get('priority_fix', 'None')}"
        )
    except Exception as e:
        rationale = f"Aggregate {aggregate:.0%} (weighted) | Comment error: {str(e)[:60]}"

    try:
        mlflow.log_metric("overall_weighted_score", aggregate)
    except Exception:
        pass

    return Feedback(value=round(aggregate, 3), rationale=rationale)


# ── 5. Docker Build Assessment ────────────────────────────────────────────────

@scorer
def docker_build_assessment(outputs) -> Feedback:
    """Качество Docker-файлов (LLM) + время сборки образа."""
    docker_files = {}
    build_time = None

    if isinstance(outputs, dict):
        docker_files = outputs.get("docker_files", {})
        build_time = outputs.get("build_time_seconds")

    if not docker_files and DOCKER_DIR.exists():
        for fp in DOCKER_DIR.iterdir():
            if fp.is_file():
                try:
                    docker_files[fp.name] = fp.read_text(encoding="utf-8")
                except Exception:
                    pass

    if not docker_files:
        return Feedback(value=0.0, rationale="Docker files not found")

    files_text = "\n\n".join(
        f"=== {name} ===\n{content}"
        for name, content in docker_files.items()
    )

    try:
        prompt = (
            "Ты DevOps-эксперт. Оцени эти Docker-файлы по шкале 0-10:\n\n"
            + files_text[:3000]
            + "\n\nКритерии:\n"
            "- correctness: корректность синтаксиса и конфигурации\n"
            "- security: безопасность (нет root, минимальный образ)\n"
            "- best_practices: best practices (layer caching, .dockerignore, restart)\n"
            "- completeness: наличие всех нужных файлов\n\n"
            'ТОЛЬКО JSON: {"correctness": 8, "security": 6, "best_practices": 7, "completeness": 9}'
        )
        response = judge_model.invoke(prompt)
        scores = json.loads(response.content.strip())
        quality = (
            scores.get("correctness", 5)
            + scores.get("security", 5)
            + scores.get("best_practices", 5)
            + scores.get("completeness", 5)
        ) / 4 / 10
    except Exception:
        quality = 0.5
        scores = {}

    if build_time is None:
        t0 = _time.time()
        code, _, err = run_cmd("docker-compose build --no-cache", cwd=DOCKER_DIR.resolve())
        build_time = _time.time() - t0
        build_ok = (code == 0)
    else:
        build_ok = True

    time_score = max(0.0, min(1.0, 1.0 - (build_time - 30) / 270))
    build_status = "✅ успешно" if build_ok else "❌ ошибка"
    final = quality * 0.7 + time_score * 0.3

    rationale = (
        f"Docker quality: Corr {scores.get('correctness','?')}/10, "
        f"Sec {scores.get('security','?')}/10, "
        f"BP {scores.get('best_practices','?')}/10, "
        f"Compl {scores.get('completeness','?')}/10 | "
        f"Build: {build_status} за {build_time:.1f}с"
    )
    SCORES_CACHE['docker_build_assessment'] = round(final, 3)
    return Feedback(value=round(final, 3), rationale=rationale)


# ── 6. Webpage Quality Assessment ────────────────────────────────────────────

@scorer
def webpage_quality_assessment(outputs) -> Feedback:
    """UI/UX, адаптивность, функционал страницы (Gemma-судья)."""
    web_files = {}
    if isinstance(outputs, dict):
        files = outputs.get("files", {})
        web_files = {k: v for k, v in files.items()
                     if k.endswith((".html", ".css", ".js"))}

    if not web_files and OUTPUT_DIR.exists():
        for fp in OUTPUT_DIR.iterdir():
            if fp.is_file() and fp.suffix in (".html", ".css", ".js"):
                try:
                    web_files[fp.name] = fp.read_text(encoding="utf-8")
                except Exception:
                    pass

    if not web_files:
        return Feedback(value=0.0, rationale="No web files found")

    gemma_judge = ChatOpenAI(
        base_url=__import__("os").getenv("OPENAI_API_HOST"),
        api_key=__import__("os").getenv("OPENAI_API_KEY"),
        model="google/gemma-3-27b-it",
        temperature=0.3,
    )

    files_text = "\n\n".join(
        f"=== {name} ===\n{content[:1500]}"
        for name, content in web_files.items()
    )

    try:
        prompt = (
            "Ты UX/frontend эксперт. Оцени веб-страницу по шкале 0-10:\n\n"
            + files_text[:4000]
            + "\n\nКритерии:\n"
            "- ui_design: визуальное оформление и структура\n"
            "- ux_usability: удобство использования\n"
            "- responsiveness: адаптивность (mobile-friendly)\n"
            "- functionality: правильность реализации функционала\n"
            "- code_quality: чистота и читаемость кода\n\n"
            'ТОЛЬКО JSON: {"ui_design": 7, "ux_usability": 8, "responsiveness": 6, "functionality": 8, "code_quality": 7}'
        )
        response = gemma_judge.invoke(prompt)
        scores = json.loads(response.content.strip())

        avg = (
            scores.get("ui_design", 5)
            + scores.get("ux_usability", 5)
            + scores.get("responsiveness", 5)
            + scores.get("functionality", 5)
            + scores.get("code_quality", 5)
        ) / 5 / 10

        rationale = (
            f"[Gemma judge] UI {scores.get('ui_design','?')}/10, "
            f"UX {scores.get('ux_usability','?')}/10, "
            f"Responsive {scores.get('responsiveness','?')}/10, "
            f"Func {scores.get('functionality','?')}/10, "
            f"Code {scores.get('code_quality','?')}/10"
        )
        SCORES_CACHE['webpage_quality_assessment'] = round(avg, 3)
        return Feedback(value=round(avg, 3), rationale=rationale)

    except Exception as e:
        return Feedback(value=0.5, rationale=f"Gemma judge error: {str(e)[:80]}")


# ── 7. Agent Timing Metric ────────────────────────────────────────────────────

@scorer
def agent_timing_metric(outputs) -> Feedback:
    """Время работы каждого агента, логируется в MLflow."""
    if not AGENT_TIMINGS:
        return Feedback(value=0.5, rationale="No agent timing data. Use timed_run() wrapper.")

    scores = []
    parts = []
    for agent_name, elapsed in AGENT_TIMINGS.items():
        s = max(0.0, min(1.0, 1.0 - (elapsed - 60) / 240))
        scores.append(s)
        parts.append(f"{agent_name}: {elapsed:.1f}с")
        try:
            mlflow.log_metric(f"agent_time_{agent_name}", elapsed)
        except Exception:
            pass

    avg_score = sum(scores) / len(scores)
    total_time = sum(AGENT_TIMINGS.values())
    rationale = "Времена агентов: " + ", ".join(parts) + f" | Итого: {total_time:.1f}с"
    SCORES_CACHE['agent_timing_metric'] = round(avg_score, 3)
    return Feedback(value=round(avg_score, 3), rationale=rationale)


# ── 8. Test Results Metric ────────────────────────────────────────────────────

@scorer
def test_results_metric(outputs) -> Feedback:
    """Пройдено/провалено тестов (pytest или smoke-тесты)."""
    test_files = []
    if OUTPUT_DIR.exists():
        test_files = (
            list(OUTPUT_DIR.glob("test_*.py")) +
            list(OUTPUT_DIR.glob("*_test.py"))
        )

    passed = failed = errors = 0

    if test_files:
        result = subprocess.run(
            ["python", "-m", "pytest", "--tb=no", "-q", str(OUTPUT_DIR)],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        m_passed = _re.search(r"(\d+) passed", output)
        m_failed = _re.search(r"(\d+) failed", output)
        m_error  = _re.search(r"(\d+) error",  output)
        passed = int(m_passed.group(1)) if m_passed else 0
        failed = int(m_failed.group(1)) if m_failed else 0
        errors = int(m_error.group(1))  if m_error  else 0
    else:
        checks = [
            ("index.html exists",     (OUTPUT_DIR / "index.html").exists()),
            ("Dockerfile exists",     (DOCKER_DIR / "Dockerfile").exists()),
            ("docker-compose exists", (DOCKER_DIR / "docker-compose.yml").exists()),
        ]
        code, out, _ = run_cmd("docker-compose ps", cwd=DOCKER_DIR.resolve())
        checks.append(("container running", "Up" in out))

        for name, ok in checks:
            if ok:
                passed += 1
            else:
                failed += 1

    total = passed + failed + errors
    if total == 0:
        return Feedback(value=0.0, rationale="No tests found or run")

    score = passed / total

    try:
        mlflow.log_metric("tests_passed", passed)
        mlflow.log_metric("tests_failed", failed)
        mlflow.log_metric("tests_errors", errors)
        mlflow.log_metric("tests_total",  total)
    except Exception:
        pass

    rationale = f"Тесты: ✅ {passed} пройдено / ❌ {failed} провалено / ⚠️ {errors} ошибок | Итого: {total}"
    SCORES_CACHE['test_results_metric'] = round(score, 3)
    return Feedback(value=round(score, 3), rationale=rationale)


# ── Список всех метрик для передачи в mlflow.genai.evaluate ──────────────────

LLM_JUDGES = [
    expert_code_review,            # читаемость, безопасность, производительность, best practices кода
    llm_functionality_check,       # соответствие требованиям, наличие багов, работоспособность
    llm_architecture_assessment,   # модульность, масштабируемость, поддерживаемость, DRY
    llm_overall_assessment,        # взвешенный агрегат всех метрик + финальный verdict LLM
    docker_build_assessment,       # качество Docker-файлов (LLM) + время сборки образа
    webpage_quality_assessment,    # UI/UX, адаптивность, функционал страницы (Gemma-судья)
    agent_timing_metric,           # время работы каждого агента, логируется в MLflow
    test_results_metric,           # пройдено/провалено тестов (pytest или smoke-тесты)
]
