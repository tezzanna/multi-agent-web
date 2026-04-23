"""
agents/agents.py
================
Создание всех агентов и supervisor.
Промпты вынесены в agents/prompts.py.
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
from agents.prompts import (
    PLANNER_PROMPT,
    DEVELOPER_PROMPT,
    EXECUTOR_PROMPT,
    DEPLOY_PROMPT,
    SUPERVISOR_PROMPT,
)

# ── Субагенты ─────────────────────────────────────────────────────────────────

planner_agent = create_agent(
    model=model,
    tools=[create_plan],
    system_prompt=PLANNER_PROMPT,
    name="planner_agent",
)

developer_agent = create_agent(
    model=model,
    tools=[write_file, save_project_file, get_api_key],
    system_prompt=DEVELOPER_PROMPT,
    name="developer_agent",
)

executor_agent = create_agent(
    model=model,
    tools=[write_docker_file, save_docker_file],
    system_prompt=EXECUTOR_PROMPT,
    name="executor_agent",
)

deploy_agent = create_agent(
    model=model,
    tools=[stop_and_remove_containers, build_and_run_docker, check_container_status],
    system_prompt=DEPLOY_PROMPT,
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
    system_prompt=SUPERVISOR_PROMPT,
    name="supervisor",
)
