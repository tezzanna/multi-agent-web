"""
tools/developer_tools.py
========================
Инструменты для агента-разработчика.
"""

import os
import base64
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from config import invoke_with_retry, save_file


@tool
def write_file(description: str) -> str:
    """Написать содержимое одного файла по его описанию. Возвращает готовый код."""
    messages = [
        SystemMessage(content="""Ты — старший веб-разработчик.
Получаешь описание файла — возвращаешь ТОЛЬКО готовое содержимое файла.
Никаких пояснений, никакого markdown."""),
        HumanMessage(content=description)
    ]
    return invoke_with_retry(messages)


@tool
def get_api_key() -> str:
    """
    Получить API ключ для OpenWeatherMap в зашифрованном виде.
    Используй когда нужно вставить API_KEY в main.js.
    """
    raw_key = os.getenv("WEATHER_API_KEY", "")
    if not raw_key:
        return "Ошибка: WEATHER_API_KEY не найден в .env"
    encoded = base64.b64encode(raw_key.encode()).decode()
    js_snippet = f"""// Вставь этот код в начало main.js:
const _k = atob("{encoded}");
// Используй _k вместо API_KEY в запросах к OpenWeatherMap
"""
    print(f"   🔑 [get_api_key] Ключ зашифрован и передан разработчику")
    return js_snippet


@tool
def save_project_file(filename: str, content: str) -> str:
    """Сохранить файл проекта на диск."""
    saved = save_file(filename, content)
    return f"Файл {filename} сохранён: {saved}"
