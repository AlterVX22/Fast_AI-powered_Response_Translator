import openai
import os
import logging
from typing import Optional
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

# Причины отмены пар (перенесены из handlers.py)
CANCELLATION_REASONS = [
    "Ровно в это время поставили отчет по проекту ((",
    "Ребята, я заболел, завтра занятия не будет :(",
    "А чтобы хорошо трудиться, надо хорошо отдыхать!",
    "Сегодня отдыхаем :)",
    "Добрый день! Нет, сегодня еще отдыхаем!",
    "Сегодня предзащиты у 6 курса, пары не будет.",
    "Нет, занятий не будет, так как мы в командировке.",
    "Нет пары начнутся не ранее следующей недели.",
    "Со следующей недели начнутся занятия!",
    "Ребята, пересматриваем расписание. Мат моделирование по средам не будет.",
    "Уважаемые ребята! Завтра в 17:00 будет пара! (шутка)",
    "В субботу будет 😅"
]

def generate_itmo_response():
    """Генерирует два варианта ИТМО-ответа"""
    # Первый вариант - из списка причин
    reason = random.choice(CANCELLATION_REASONS)
    response1 = {
        "title": "🎓 Наша Вселенная",
        "text": f"⚠️ Всем привет!\n{reason}\n\nСо следующей недели уже совершенно точно начинаем! 😊"
    }
    
    # Второй вариант - генерируем похожий текст через ИИ
    try:
        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "Ты имитируешь преподавателя ИТМО, который отменяет пары."},
                {"role": "user", "content": f"Придумай краткую причину отмены пар немного абсурдную, похожую на эти примеры: {', '.join(CANCELLATION_REASONS)}. Только саму причину, без приветствий."}
            ],
            headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "ITMO Bot"
            },
            temperature=0.7
        )
        ai_reason = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        ai_reason = "Ребята, сегодня занятий не будет, так как... ну вы понимаете 😅"
    
    response2 = {
        "title": "🎓 О мультивселенной мало что известно...",
        "text": f"⚠️ Всем привет!\n{ai_reason}\n\nСо следующей недели уже совершенно точно начинаем! 😊"
    }
    
    return [response1, response2]

def translate_text_with_llm(text: str, target_lang: str, source_lang: str = "auto", model: Optional[str] = None) -> str:
    if not text.strip():
        return "Ошибка: пустой текст"
    
    model = model or DEFAULT_MODEL
    prompt = f"Переведи следующий текст на {target_lang}, сохраняя стиль и форматирование.\nНе добавляй пояснения. Только перевод:\n\n{text}"

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты профессиональный переводчик."},
                {"role": "user", "content": prompt}
            ],
            headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Translation Bot"
            },
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenRouter Error: {str(e)}")
        return f"Ошибка перевода: {str(e)}"