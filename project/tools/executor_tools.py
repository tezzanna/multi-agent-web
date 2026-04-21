"""
tools/executor_tools.py
=======================
Инструменты для DevOps-агента (создание Docker-файлов).
"""

import re
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from config import invoke_with_retry, save_file_docker


@tool
def write_docker_file(filename: str, description: str) -> str:
    """
    Написать содержимое одного Docker-файла.
    Аргументы: filename — имя файла, description — подробное ТЗ.
    """
    HARDCODED = {
        "Dockerfile": (
            "FROM nginx:1.27-alpine\n"
            "COPY . /usr/share/nginx/html\n"
            "EXPOSE 80\n"
        ),
        "docker-compose.yml": (
            'version: "3.9"\n\n'
            "services:\n"
            "  weather-app:\n"
            "    build:\n"
            "      context: ..\n"
            "      dockerfile: docker/Dockerfile\n"
            "    ports:\n"
            '      - "8080:80"\n'
            "    restart: always\n"
        ),
    }

    if filename in HARDCODED:
        content = HARDCODED[filename]
        print(f"   ✍️  {filename}: использован жёсткий шаблон ({len(content)} символов)")
        return content

    messages = [
        SystemMessage(content="""Ты — Senior DevOps инженер.
Возвращаешь ТОЛЬКО содержимое файла. Никакого markdown, никаких ```."""),
        HumanMessage(content=f"Файл: {filename}\nОписание: {description}")
    ]
    content = invoke_with_retry(messages)
    content = re.sub(r'^```[\w]*\n?', '', content.strip())
    content = re.sub(r'\n?```$', '', content.strip())
    print(f"   ✍️  {filename}: написан ({len(content)} символов)")
    return content


@tool
def save_docker_file(filename: str, content: str) -> str:
    """Сохранить Docker-файл на диск в папку docker."""
    saved = save_file_docker(filename, content)
    return f"Файл {filename} сохранён: {saved}"
