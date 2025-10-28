import random
import os
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from threading import Thread

# === 🔹 Настройки ===
TOKEN = "8368265900:AAHOQOeJs57zfpHOSm4594lvFsPm9VKO91c"  # токен бота
ADMIN_ID = 1078514845  # твой Telegram ID

# === 🔹 Настройки Flask ===
app = Flask(__name__)

# === 🔹 Настройки бота ===
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === 🔹 Папка с фото ===
IMAGE_FOLDER = "images"


# === 🔹 Отправка случайного фото пользователю ===
async def send_random_forecast(user_id: int):
    try:
        images = os.listdir(IMAGE_FOLDER)
        if not images:
            await bot.send_message(chat_id=ADMIN_ID, text="⚠️ Папка images пуста!")
            return

        image_path = os.path.join(IMAGE_FOLDER, random.choice(images))
        with open(image_path, "rb") as photo:
            await bot.send_photo(chat_id=user_id, photo=photo, caption="🎯 Твой прогноз готов!")

    except Exception as e:
        await bot.send_message(chat_id=ADMIN_ID, text=f"Ошибка при отправке прогноза: {e}")


# === 🔹 Flask маршруты ===
@app.route('/')
def index():
    return "✅ Бот работает!"


@app.route('/apitelegram', methods=['POST'])
async def apitelegram():
    try:
        data = await request.get_json()
        if not data:
            return "no data", 400

        text = str(data.get("text"))
        if not text:
            return "no text", 400

        # Проверяем, число ли это (ID пользователя)
        if text.isdigit():
            await send_random_forecast(int(text))
            await bot.send_message(chat_id=ADMIN_ID, text=f"📩 Отправлен прогноз пользователю {text}")
        else:
            # Если не число, значит это сумма пополнения
            await bot.send_message(chat_id=ADMIN_ID, text=f"💰 Пополнение на сумму: {text}")

        return "ok", 200
    except Exception as e:
        print("Ошибка /apitelegram:", e)
        return "error", 500


# === 🔹 Обработчик /start ===
@dp.message(CommandStart())
async def start_cmd(message: Message):
    text = (
        "📲Для начала необходимо провести регистрацию на 1win. Чтобы бот успешно проверил регистрацию, нужно соблюсти важные условия:\n\n"
        "1️⃣ Аккаунт обязательно должен быть НОВЫМ! Если у вас уже есть аккаунт и при нажатии на кнопку «РЕГИСТРАЦИЯ» "
        "вы попадаете на старый, необходимо выйти и зарегистрироваться заново!\n\n"
        "2️⃣ Чтобы бот смог проверить вашу регистрацию, обязательно нужно ввести промокод <b>\"\"</b> при регистрации!\n\n"
        "3️⃣ Внести депозит на минимальную сумму!\n\n"
        "После РЕГИСТРАЦИИ бот автоматически переведёт вас к следующему шагу ✅"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 РЕГИСТРАЦИЯ", url="https://1wilib.life/casino/list/4?p=ly1f"))
    await message.answer(text, reply_markup=markup)


# === 🔹 Запуск Flask и Telegram одновременно ===
def run_flask():
    app.run(host="0.0.0.0", port=5000)


async def run_telegram():
    await dp.start_polling(bot)


if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(run_telegram())

