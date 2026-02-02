"""
cashback_history.py

Модуль для работы с историей выплат кэшбэков.
Сохраняет данные в файл paid_cashbacks.json
"""
import json
import os
from typing import List

HISTORY_FILE = "../paid_cashbacks.json"

def load_paid_cashbacks() -> List[str]:
    """Загружает список уже выплаченных кэшбэков из файла"""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_paid_cashback(shk_id: str):
    """Добавляет SHK-ID в список выплаченных кэшбэков"""
    paid = load_paid_cashbacks()
    if shk_id not in paid:
        paid.append(shk_id)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(paid, f, ensure_ascii=False, indent=2)

def is_cashback_paid(shk_id: str) -> bool:
    """Проверяет, был ли уже выплачен кэшбэк для данного SHK-ID"""
    return shk_id in load_paid_cashbacks()