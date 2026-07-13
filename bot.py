import telebot
import requests
from flask import Flask
import threading
import json

BOT_TOKEN = "8769849422:AAFQQvHYP2gLlSXcxjgmO1YsERGInkGCo1k"  # Вставь свой токен

bot = telebot.TeleBot(BOT_TOKEN)

user_history = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Привет! Я бесплатный ИИ-помощник на LocalAI!\n\nЗадавай любой вопрос!")

@bot.message_handler(commands=['clear'])
def clear_history(message):
    chat_id = str(message.chat.id)
    if chat_id in user_history:
        user_history[chat_id] = []
    bot.reply_to(message, "🧹 История очищена!")

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

        # Используем общедоступный LocalAI эндпоинт
        url = "https://localai.io/api/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "llama3",
            "messages": messages_to_send,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if response.status_code == 200:
            reply = data["choices"][0]["message"]["content"]
            user_history[chat_id].append({"role": "assistant", "content": reply})
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, f"❌ Ошибка API: {data}")

    except requests.exceptions.Timeout:
        bot.reply_to(message, "❌ Превышено время ожидания. Попробуй ещё раз.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Заглушка для Render
app = Flask(name)

@app.route('/')
def home():
    return "✅ Бот работает!"

def run_bot():
    print("🤖 Бот запущен...")
    bot.infinity_polling()

if name == "main":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
