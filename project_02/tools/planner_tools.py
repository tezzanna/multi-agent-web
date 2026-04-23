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
from agents.prompts import PLANNER_TOOL_SYSTEM


@tool
def create_plan(query: str) -> str:
    """Создать план разработки веб-приложения. Возвращает JSON-список файлов."""
    messages = [
        SystemMessage(content=PLANNER_TOOL_SYSTEM),
        HumanMessage(content=query)
    ]
    return invoke_with_retry(messages)
