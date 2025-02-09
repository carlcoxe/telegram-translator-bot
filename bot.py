import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from googletrans import Translator
import asyncio

# ✅ Получаем токен из переменных окружения (Railway использует API_bot)
TOKEN = os.getenv("API_bot")

# Проверяем, есть ли токен
if not TOKEN:
    raise ValueError("❌ Ошибка: Токен бота не найден! Убедитесь, что переменная API_bot задана в Railway.")

# ✅ Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Логирование
logging.basicConfig(level=logging.INFO)

# ✅ Переводчик
translator = Translator()

# ✅ Доступные языки перевода
LANGUAGES_MAP = {
    "Русский": "ru",
    "Английский": "en",
    "Немецкий": "de",
    "Французский": "fr"
}

# ✅ Словарь для хранения выбранного языка пользователей
user_languages = {}

# ✅ Клавиатура выбора языка
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=lang)] for lang in LANGUAGES_MAP.keys()],
    resize_keyboard=True
)

# 📌 Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я бот-переводчик. Используй команду /lang, чтобы выбрать язык перевода.")

# 📌 Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("📖 Отправь мне текст, и я переведу его на выбранный тобой язык.\nВыбери язык командой /lang.")

# 📌 Обработчик команды /lang
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    await message.answer("🌍 Выбери язык для перевода:", reply_markup=lang_keyboard)

# 📌 Обработчик выбора языка
@dp.message(lambda message: message.text in LANGUAGES_MAP)
async def select_language(message: types.Message):
    user_languages[message.from_user.id] = LANGUAGES_MAP[message.text]
    await message.answer(f"✅ Язык перевода установлен: {message.text}")

# 📌 Обработчик перевода сообщений
@dp.message()
async def translate_message(message: types.Message):
    user_id = message.from_user.id
    target_lang = user_languages.get(user_id, "en")  # По умолчанию переводим на английский

    try:
        # Определяем язык входного текста
        detected_lang = translator.detect(message.text).lang

        # Если язык уже совпадает с целевым
        if detected_lang == target_lang:
            await message.answer("🔹 Твой текст уже на выбранном языке!")
            return

        # Переводим текст
        translated_text = translator.translate(message.text, dest=target_lang).text
        await message.answer(f"📜 Перевод:\n<code>{translated_text}</code>")
    
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.answer("⚠️ Ошибка перевода. Попробуйте позже.")

# 📌 Обработчик ошибок
@dp.errors()
async def error_handler(update, exception):
    logging.error(f"❌ Ошибка: {exception}")
    return True  # Чтобы бот не падал

# 📌 Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляем старые апдейты
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

