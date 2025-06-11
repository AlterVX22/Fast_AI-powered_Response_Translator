import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    filters, ConversationHandler
)
from bot.handlers import (
    start, help_command, handle_text, handle_language_selection,handle_itmo_text,
    itmo_command, STATE_SELECT_OUTPUT_LANG, STATE_ENTER_TEXT, STATE_ENTER_ITMO_TEXT
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    if not TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не задан в .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text),
            CommandHandler("itmo", itmo_command)  # Добавляем команду как entry point
        ],
        states={
            STATE_SELECT_OUTPUT_LANG: [
                CallbackQueryHandler(handle_language_selection)
            ],
            STATE_ENTER_TEXT: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)
            ],
            STATE_ENTER_ITMO_TEXT: [  # Добавляем новое состояние
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_itmo_text)
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("itmo", itmo_command)
        ],
        per_message=False
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("itmo", itmo_command))  # Оставляем для прямого вызова
    
    print("Бот запущен.")
    app.run_polling()
if __name__ == "__main__":
    main()