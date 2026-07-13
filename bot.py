import os
import telebot
from openai import OpenAI
from flask import Flask
import threading

# ===== ВСТАВЬ СВОИ КЛЮЧИ СЮДА =====
BOT_TOKEN = "8769849422:AAFQQvHYP2gLlSXcxjgmO1YsERGInkGCo1k"  # Например: 123456:ABCdef
AGNES_API_KEY = "sk-3d0gk4OWkZIcfYAmXZT1NSunwhn2NF8qYYW6kCuUZ34H0ctu"   # Например: sk-3d0...
# ====================================

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    api_key=AGNES_API_KEY,
    base_url="https://apihub.agnes-ai.com/v1"
)

user_history = {}

# ===== КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Привет! Я ИИ-помощник на базе Agnes AI!\n\n✍️ Задавай любой вопрос!")

@bot.message_handler(commands=['clear'])
def clear_history(message):
    chat_id = str(message.chat.id)
    if chat_id in user_history:
        user_history[chat_id] = []
    bot.reply_to(message, "🧹 История диалога очищена!")

@bot.message_handler(func=lambda msg: True)
def answer(message):
    chat_id = str(message.chat.id)
    user_text = message.text

    if chat_id not in user_history:
        user_history[chat_id] = []

    user_history[chat_id].append({"role": "user", "content": user_text})
    messages_to_send = user_history[chat_id][-10:]

    try:
        bot.send_chat_action(message.chat.id, "typing")
        response = client.chat.completions.create(
            model="agnes-2.0-flash",
            messages=messages_to_send,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        user_history[chat_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# ===== ЗАГЛУШКА ДЛЯ RENDER =====
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает! 😊"

def run_bot():
    print("🤖 Бот запущен...")
    bot.infinity_polling()

if name == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
