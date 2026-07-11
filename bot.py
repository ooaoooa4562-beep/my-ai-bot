import os
import telebot
from openai import OpenAI

# ===== НАСТРОЙКИ =====
# Вставь сюда свой API-ключ от Agnes AI
AGNES_API_KEY = "sk-3d0gk4OWkZIcfYAmXZT1NSunwhn2NF8qYYW6kCuUZ34H0ctu"

# Токен бота из .env (или впиши сюда, если хочешь)
BOT_TOKEN = "8769849422:AAFQQvHYP2gLlSXcxjgmO1YsERGInkGCo1k"  # Если не работает — замени на "твой_токен"

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=AGNES_API_KEY,
    base_url="https://apihub.agnes-ai.com/v1"
)

# Словарь для хранения истории диалогов
history = {}

# ===== КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 Привет! Я твой личный ИИ-помощник на базе Agnes AI!\n\n"
        "✍️ Пиши мне всё, что хочешь спросить или обсудить, "
        "а я постараюсь ответить максимально полезно и интересно! 😊\n\n"
        "💡 Команды:\n"
        "/start — показать это сообщение\n"
        "/clear — очистить историю диалога"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['clear'])
def clear_history(message):
    chat_id = message.chat.id
    if chat_id in history:
        history[chat_id] = []
    bot.reply_to(message, "🧹 История диалога очищена! Можем начать сначала 😉")

# ===== ОСНОВНОЙ ОТВЕТЧИК =====
@bot.message_handler(func=lambda msg: True)
def answer(message):
    chat_id = message.chat.id

    if chat_id not in history:
        history[chat_id] = []

    # Добавляем сообщение пользователя в историю
    history[chat_id].append({"role": "user", "content": message.text})

    # Берём последние 10 сообщений для контекста
    messages_to_send = history[chat_id][-10:]

    try:
        bot.send_chat_action(chat_id, "typing")

        response = client.chat.completions.create(
            model="agnes-2.0-flash",
            messages=messages_to_send,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        # Сохраняем ответ бота в историю
        history[chat_id].append({"role": "assistant", "content": reply})

        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}. Попробуй ещё раз!")

# ===== ЗАПУСК =====
print("✅ Бот на Agnes AI запущен и готов к работе!")
bot.infinity_polling()