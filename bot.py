import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from flask import Flask, request

# --- Твой токен бота ---
BOT_TOKEN = "8368265900:AAHOQOeJs57zfpHOSm4594lvFsPm9VKO91c"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Flask сервер для Render ---
app = Flask(__name__)

# --- Обработка команды /start ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = [[types.KeyboardButton(text="📲 Регистрация")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        "👋 Привет! Нажми на кнопку ниже, чтобы зарегистрироваться:",
        reply_markup=keyboard
    )

# --- Кнопка Регистрация ---
@dp.message(F.text == "📲 Регистрация")
async def send_reg_link(message: types.Message):
    reg_link = "https://1wincpz.top/casino/list?open=register"
    await message.answer(
        f"🔗 Вот твоя ссылка для регистрации: {reg_link}\n\nПосле регистрации подожди немного — бот отправит тебе прогноз 😉"
    )

# --- POSTBACK от 1win (user_id и amount) ---
@app.route('/postback', methods=['GET', 'POST'])
def postback():
    try:
        data = request.args or request.form
        user_id = data.get("user_id")
        amount = data.get("amount")

        # Если есть user_id — шлем фото
        if user_id:
            asyncio.run(send_random_image(user_id))

        # Если есть сумма — шлем сообщение
        if user_id and amount:
            asyncio.run(send_amount_info(user_id, amount))

        return "ok", 200
    except Exception as e:
        print("Ошибка postback:", e)
        return "error", 500

# --- Отправка случайного фото из папки images ---
async def send_random_image(user_id):
    folder = "images"
    images = os.listdir(folder)
    if not images:
        return
    random_img = random.choice(images)
    path = os.path.join(folder, random_img)
    await bot.send_photo(chat_id=user_id, photo=open(path, "rb"))

# --- Отправка суммы (если есть) ---
async def send_amount_info(user_id, amount):
    text = f"💸 Сумма: {amount}₸"
    await bot.send_message(chat_id=user_id, text=text)

# --- Запуск aiogram ---
async def main():
    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)

# --- Flask сервер ---
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()
    asyncio.run(main())
