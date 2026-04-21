"""
tools/planner_tools.py
======================
Инструменты для агента-планировщика.
"""

import os
import base64
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from config import invoke_with_retry, save_file, save_file_docker


@tool
def create_plan(query: str) -> str:
    """Создать план разработки веб-приложения. Возвращает JSON-список файлов."""
    messages = [
        SystemMessage(content="""Ты — старший планировщик проектов.
Разбей задачу на конкретные файлы. Отвечай ТОЛЬКО валидным JSON массивом.
Каждый элемент: {"filename": "имя файла", "description": "что должно быть внутри"}

ВАЖНО:
- каждый файл ровно один раз
- максимум один js-файл (main.js)
- сначала index.html со всеми id-элементами
- в описаниях css/js указывай какие id/классы использовать из index.html
- в main.js разработчик получит API ключ через инструмент get_api_key
"""),
        HumanMessage(content=query)
    ]
    return invoke_with_retry(messages)
