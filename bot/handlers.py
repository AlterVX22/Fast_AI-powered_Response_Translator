from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import requests
import os
from dotenv import load_dotenv
import random
import openai

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

# Определяем состояния
(
    STATE_SELECT_INPUT_LANG,
    STATE_SELECT_OUTPUT_LANG,
    STATE_ENTER_TEXT
) = range(3)

LANGUAGES = {
    "🇬🇧 Английский": "English",
    "🇫🇷 Французский": "French",
    "🇩🇪 Немецкий": "German",
    "🇪🇸 Испанский": "Spanish",
    "🇨🇳 Китайский": "Chinese"
}

# Причины отмены пар
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

start_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🔤 Начать перевод"), KeyboardButton("ℹ️ Помощь")],
        [KeyboardButton("🏫 ИТМО")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def delete_message_with_animation(context, chat_id, message_id):
    """Удаление сообщения с анимацией (эффект Таноса)"""
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-переводчик. Нажми \"🔤 Начать перевод\", чтобы начать.",
        reply_markup=start_buttons
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "🔤 Начать перевод - перевод текста на выбранный язык\n"
        "🏫 ИТМО - узнать, как звучит ИТМО\n"
        "ℹ️ Помощь - это сообщение",
        reply_markup=start_buttons
    )
    return ConversationHandler.END


async def itmo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton("Оставь надежду, всяк сюда входящий", callback_data="output_itmo")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "Нажмите кнопку ниже, чтобы узнать, почему сегодня не будет пар:",
        reply_markup=reply_markup
    )
    return STATE_SELECT_OUTPUT_LANG

async def handle_itmo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🔤 Начать перевод":
        buttons = [[InlineKeyboardButton(lang, callback_data=f"output_{code}")] 
                  for lang, code in LANGUAGES.items()]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Выберите язык перевода:", reply_markup=reply_markup)
        return STATE_SELECT_OUTPUT_LANG

    elif text == "ℹ️ Помощь":
        return await help_command(update, context)

    elif text == "🏫 ИТМО":
        return await itmo_command(update, context)

    elif context.user_data.get("expecting_text", False):
        context.user_data["expecting_text"] = False
        target_lang = context.user_data.get("target_lang")
        
        translation = request_translation(text, target_lang)
        await update.message.reply_text(
            f"Перевод на {target_lang}:\n{translation}",
            reply_markup=start_buttons
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Используйте кнопки для навигации",
        reply_markup=start_buttons
    )
    return ConversationHandler.END


async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("output_"):
        lang_code = query.data.split("_")[1]
        
        if lang_code == "itmo":
            await delete_message_with_animation(context, query.message.chat_id, query.message.message_id)
            
            try:
                response = requests.get(f"{BACKEND_URL}/itmo-translate", timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    responses = data.get("responses", [])
                    
                    if len(responses) >= 2:
                        response_text = "\n\n".join(
                            f"{r['title']}:\n\n{r['text']}" for r in responses
                        )
                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text=response_text,
                            reply_markup=start_buttons
                        )
                    else:
                        raise Exception("Неверный формат ответа от сервера")
                else:
                    raise Exception(f"Ошибка сервера: {response.status_code}")
            except Exception as e:
                #logger.error(f"ITMO translation error: {e}")
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Произошла ошибка при генерации ИТМО-ответов",
                    reply_markup=start_buttons
                )
        else:
            context.user_data["target_lang"] = lang_code
            context.user_data["expecting_text"] = True
            
            await delete_message_with_animation(context, query.message.chat_id, query.message.message_id)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Введите текст для перевода:",
                reply_markup=ReplyKeyboardRemove()
            )
        return ConversationHandler.END
    
    return ConversationHandler.END


def request_translation(text: str, target_lang: str) -> str:
    if not BACKEND_URL:
        return "❌ Ошибка: сервер перевода не настроен"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/translate",
            json={"text": text, "target_lang": target_lang},
            timeout=20
        )
        return response.json().get("result", "❌ Пустой ответ от сервера") if response.status_code == 200 else f"❌ Ошибка сервера ({response.status_code})"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"