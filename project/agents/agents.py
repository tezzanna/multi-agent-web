"""
agents/agents.py
================
Создание всех агентов и supervisor.
Каждый агент изолирован — знает только свои инструменты.
"""

from langchain.agents import create_agent
from langchain.tools import tool

from config import model, OUTPUT_DIR, DOCKER_DIR
from tools import (
    create_plan,
    write_file, get_api_key, save_project_file,
    write_docker_file, save_docker_file,
    stop_and_remove_containers, build_and_run_docker, check_container_status,
)

# ── Субагенты ─────────────────────────────────────────────────────────────────

planner_agent = create_agent(
    model=model,
    tools=[create_plan],
    system_prompt="Ты — агент-планировщик. Вызови create_plan и верни JSON-план файлов проекта.",
    name="planner_agent",
)

developer_agent = create_agent(
    model=model,
    tools=[write_file, save_project_file, get_api_key],
    system_prompt="""Ты — агент-разработчик. Получаешь план в виде JSON-списка файлов.
Для каждого файла:
1. Если файл main.js — сначала вызови get_api_key чтобы получить зашифрованный ключ
2. Вызови write_file с описанием файла (включи в описание полученный js_snippet)
3. Вызови save_project_file с именем файла и содержимым
Обработай ВСЕ файлы из плана.""",
    name="developer_agent",
)

executor_agent = create_agent(
    model=model,
    tools=[write_docker_file, save_docker_file],
    system_prompt="""Ты — DevOps-разработчик. Создай файлы для Docker-деплоя.

Создай СТРОГО ЭТИ файлы по порядку, для каждого:
1. Вызови write_docker_file(filename, description)
2. Вызови save_docker_file(filename, content)

Список файлов:
- filename: "Dockerfile"
  description: "Контейнер для раздачи статических файлов (html, css, js). Контекст сборки — папка с фронтендом."

- filename: "docker-compose.yml"
  description: "Запуск контейнера weather-app, порт 8080, context: .. , dockerfile: docker/Dockerfile, restart: always"

- filename: ".env.example"
  description: "OPENAI_API_HOST, OPENAI_API_KEY, WEATHER_API_KEY с пустыми значениями"

- filename: ".dockerignore"
  description: ".env, .git, __pycache__, *.pyc, docker/"

Обработай ВСЕ 4 файла.""",
    name="executor_agent",
)

deploy_agent = create_agent(
    model=model,
    tools=[stop_and_remove_containers, build_and_run_docker, check_container_status],
    system_prompt="""Ты — агент деплоя. Выполни строго по порядку:
1. stop_and_remove_containers("") — останови старые контейнеры
2. build_and_run_docker("") — собери и запусти новый контейнер
3. check_container_status("") — проверь что контейнер работает
Верни итоговый URL приложения.""",
    name="deploy_agent",
)

# ── Инструменты supervisor (обёртки над субагентами) ──────────────────────────

@tool
def run_planner(task: str) -> str:
    """Запустить агента-планировщика. Составляет JSON-план файлов веб-проекта.
    Передай задачу пользователя целиком."""
    result = planner_agent.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config={"recursion_limit": 20}
    )
    output = result["messages"][-1].content
    print(f"\n📋 [Planner] завершён")
    return output


@tool
def run_developer(plan: str) -> str:
    """Запустить агента-разработчика. Пишет и сохраняет все файлы фронтенда.
    Передай JSON-план от планировщика."""
    result = developer_agent.invoke(
        {"messages": [{"role": "user", "content": plan}]},
        config={"recursion_limit": 30}
    )
    output = result["messages"][-1].content
    print(f"\n👨‍💻 [Developer] завершён")
    return output


@tool
def run_executor(task: str = "Создай Docker-файлы для деплоя") -> str:
    """Запустить DevOps-агента. Создаёт Dockerfile, docker-compose.yml и вспомогательные файлы.
    Всегда передавай строку с задачей."""
    result = executor_agent.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config={"recursion_limit": 20}
    )
    output = result["messages"][-1].content
    print(f"\n🔧 [Executor] завершён")
    return output


@tool
def run_deploy(task: str = "Задеплой приложение") -> str:
    """Запустить агента деплоя. Останавливает старые контейнеры, собирает образ и запускает новый.
    Возвращает URL приложения."""
    result = deploy_agent.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config={"recursion_limit": 20}
    )
    output = result["messages"][-1].content
    print(f"\n🚀 [Deploy] завершён")
    return output


# ── Supervisor ────────────────────────────────────────────────────────────────

supervisor = create_agent(
    model=model,
    tools=[run_planner, run_developer, run_executor, run_deploy],
    system_prompt="""Ты — менеджер команды разработки. Выполняй СТРОГО по порядку:

1. run_planner      — составит план файлов проекта
2. run_developer    — напишет и сохранит файлы фронтенда (передай ему план от планировщика)
3. run_executor     — создаст Dockerfile и docker-compose.yml
4. run_deploy       — остановит старые контейнеры, соберёт и запустит новый

НЕ пропускай ни одного агента.
НЕ завершай работу пока все четыре агента не выполнены.
В финальном ответе обязательно укажи URL приложения.""",
    name="supervisor",
)
