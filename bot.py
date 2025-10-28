import os
import random
import asyncio
import threading
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# === Настройки ===
TOKEN = "8368265900:AAHOQOeJs57zfpHOSm4594lvFsPm9VKO91c"      # <-- вставь сюда токен от @BotFather
ADMIN_ID = 1078514845             # <-- твой Telegram ID (Азат)
REF_LINK = "https://1wilib.life/casino/list/4?p=ly1f"  # <-- твоя партнёрская ссылка

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)

# === Кнопка регистрации ===
reg_button = KeyboardButton("📲 Регистрация")
reg_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(reg_button)

# === Приветственное сообщение ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (
        "📲Для начала необходимо провести регистрацию на 1win. Чтобы бот успешно проверил регистрацию, нужно соблюсти важные условия:\n\n"
        "1️⃣ Аккаунт обязательно должен быть НОВЫМ! Если у вас уже есть аккаунт и при нажатии на кнопку «РЕГИСТРАЦИЯ» вы попадаете на старый, "
        "необходимо выйти с него и заново нажать на кнопку «РЕГИСТРАЦИЯ», после чего по новой зарегистрироваться!\n\n"
        "2️⃣ Чтобы бот смог проверить вашу регистрацию, обязательно нужно ввести промокод при регистрации!\n\n"
        "3️⃣ Внести депозит на минимальную сумму!\n\n"
        "После РЕГИСТРАЦИИ бот автоматически переведёт вас к следующему шагу ✅"
    )
    await message.answer(text, reply_markup=reg_markup)

# === Обработка кнопки ===
@dp.message_handler(lambda message: message.text == "📲 Регистрация")
async def register(message: types.Message):
    link = f"{REF_LINK}&tag={message.from_user.id}"
    await message.answer(f"🔗 Перейди по ссылке и зарегистрируйся:\n{link}")

# === Flask: получение постбэков от 1Win ===
@app.route('/')
def index():
    return "✅ 1win bot работает!"

@app.route('/postback', methods=['POST'])
def postback():
    data = request.json
    if not data:
        return "no data"
    
    user_id = data.get("subid")
    amount = data.get("amount")

    if user_id:
        asyncio.run(send_forecast(user_id, amount))
    return "ok"

# === Отправка прогноза ===
async def send_forecast(user_id, amount=None):
    try:
        folder = "images"
        files = [f for f in os.listdir(folder) if f.endswith((".jpg", ".png"))]
        if not files:
            await bot.send_message(chat_id=ADMIN_ID, text="⚠️ В папке images нет фото!")
            return

        photo_path = os.path.join(folder, random.choice(files))
        caption = "🎯 Твой прогноз! Удачи 🍀"

        if amount:
            caption += f"\n💰 Пополнение: {amount}₸"

        await bot.send_photo(chat_id=user_id, photo=open(photo_path, "rb"), caption=caption)
        await bot.send_message(chat_id=ADMIN_ID, text=f"✅ Отправлен прогноз пользователю {user_id}")

    except Exception as e:
        await bot.send_message(chat_id=ADMIN_ID, text=f"❌ Ошибка при отправке прогноза: {e}")

# === Запуск Flask и Telegram одновременно ===
def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_telegram():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_telegram()
