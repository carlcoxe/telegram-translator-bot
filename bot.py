import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties  # ✅ Новый способ установки parse_mode
from googletrans import Translator

# ✅ Получаем токен (API_bot)
TOKEN = os.getenv("API_bot")

# 🔍 Отладка: Проверяем, загружен ли токен (выведет в логи)
if not TOKEN:
    raise ValueError("❌ Ошибка: Токен не найден! Проверьте Railway → Variables.")

logging.basicConfig(level=logging.INFO)

# ✅ Инициализация бота (Используем новый способ установки parse_mode)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
translator = Translator()

# ✅ Доступные языки перевода
LANGUAGES_MAP = {"Русский": "ru", "Английский": "en", "Немецкий": "de", "Французский": "fr"}
user_languages = {}

# ✅ Клавиатура выбора языка
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=lang)] for lang in LANGUAGES_MAP.keys()],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я бот-переводчик. Используй команду /lang, чтобы выбрать язык.")

@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    await message.answer("🌍 Выбери язык перевода:", reply_markup=lang_keyboard)

@dp.message(lambda message: message.text in LANGUAGES_MAP)
async def select_language(message: types.Message):
    user_languages[message.from_user.id] = LANGUAGES_MAP[message.text]
    await message.answer(f"✅ Язык установлен: {message.text}")

@dp.message()
async def translate_message(message: types.Message):
    user_id = message.from_user.id
    target_lang = user_languages.get(user_id, "en")

    try:
        detected_lang = translator.detect(message.text).lang
        if detected_lang == target_lang:
            await message.answer("🔹 Твой текст уже на нужном языке!")
            return

        translated_text = translator.translate(message.text, dest=target_lang).text
        await message.answer(f"📜 Перевод:\n<code>{translated_text}</code>")
    
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.answer("⚠️ Ошибка перевода.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


