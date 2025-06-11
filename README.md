# Читай МЕНЯ 
FART -  Fast AI-powered Response Translator <br>

**Проект имеет следующую файловую структуру:**
```
├── backend/                   # Основной backend-код проекта
│   ├── __init__.py
│   ├── main.py                # Точка входа backend-части
│   └── llm_utils.py           # Утилиты для работы с языковыми моделями
├── bot/                       # Телеграм-бот часть проекта
│   ├── __init__.py
│   ├── main.py                # Точка входа бота
│   └── handlers.py            # Обработчики команд и сообщений
├── .env                       # Этот файл необходимо создать!
├── requirements.txt           
└── .gitignore                 
```
<br>

**Для корректного запуска :** <br>

Клонируйте репозиторий
```
git clone https://github.com/AlterVX22/Fast_AI-powered_Response_Translator.git
```

Создайте файл .env со следующим содержимым:
```
OPENROUTER_API_KEY=Ваш_API_Ключ              # Можно создать на сайте https://openrouter.ai/
TELEGRAM_BOT_TOKEN=Токен_вашего_бота         # Можно создать у @BotFather
BACKEND_URL=http://localhost:8000
```

Установите все зависимости:
```
pip install -r requirements.txt
```

Запустите следующие команды:
```python
python -m  backend.main
```
```python
 python -m  bot.main
```

**Демонстрация работы:**

![Пример](https://github.com/AlterVX22/Fast_AI-powered_Response_Translator/blob/main/demo.gif)
