# Мультиагентная система генерации веб-приложений

## Структура проекта

```
project/
│
├── main.py               # Точка входа: генерация + оценка
├── evaluate_only.py      # Только оценка уже готовых файлов
├── .env.example          # Шаблон переменных окружения
│
├── config/
│   ├── __init__.py
│   └── settings.py       # Модели, MLflow, директории, утилиты
│
├── tools/
│   ├── __init__.py
│   ├── planner_tools.py  # create_plan
│   ├── developer_tools.py # write_file, get_api_key, save_project_file
│   ├── executor_tools.py  # write_docker_file, save_docker_file
│   └── deploy_tools.py   # stop_and_remove_containers, build_and_run_docker, check_container_status
│
├── agents/
│   ├── __init__.py
│   └── agents.py         # planner, developer, executor, deploy, supervisor
│
├── metrics/
│   ├── __init__.py
│   └── scorers.py        # Все 8 метрик + LLM_JUDGES + timed_run
│
└── scripts/
    └── demo_00/          # Сюда генерируются файлы проекта
        └── docker/       # Сюда генерируются Docker-файлы
```

## Быстрый старт

```bash
# 1. Скопировать и заполнить переменные окружения
cp .env.example .env

# 2. Установить зависимости
pip install langchain langchain-openai mlflow python-dotenv

# 3. Запустить полный пайплайн
python main.py

# 4. Запустить с кастомным запросом
python main.py --query "Создай todo-приложение с localStorage"

# 5. Переоценить уже сгенерированные файлы
python evaluate_only.py
```

## Агенты

| Агент | Инструменты | Задача |
|---|---|---|
| planner_agent | create_plan | JSON-план файлов проекта |
| developer_agent | write_file, save_project_file, get_api_key | Пишет и сохраняет HTML/CSS/JS |
| executor_agent | write_docker_file, save_docker_file | Создаёт Docker-файлы |
| deploy_agent | stop_and_remove_containers, build_and_run_docker, check_container_status | Деплоит контейнер |
| supervisor | run_planner, run_developer, run_executor, run_deploy | Координирует всех |

## Метрики оценки

| Метрика | Что оценивает | Вес в итоге |
|---|---|---|
| expert_code_review | Читаемость, безопасность, производительность, BP | 20% |
| llm_functionality_check | Соответствие требованиям, баги, работоспособность | 20% |
| llm_architecture_assessment | Модульность, масштабируемость, DRY | 15% |
| docker_build_assessment | Качество Docker + время сборки | 15% |
| webpage_quality_assessment | UI/UX, адаптивность (Gemma-судья) | 15% |
| agent_timing_metric | Время работы каждого агента | 8% |
| test_results_metric | Пройдено/провалено тестов | 7% |
| llm_overall_assessment | Взвешенный агрегат + verdict | — |

## Замер времени агентов

Чтобы метрика `agent_timing_metric` работала, оберни запуск supervisor через `timed_run`:

```python
from metrics import timed_run
from agents import supervisor

result = timed_run(
    "supervisor",
    supervisor.invoke,
    {"messages": [{"role": "user", "content": query}]},
    config={"recursion_limit": 80}
)
```
