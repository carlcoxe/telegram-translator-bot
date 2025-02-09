import os
import logging
import asyncio
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from googletrans import Translator

TOKEN = os.getenv("API_bot")  # Токен теперь берём из Railway
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
translator = Translator()

# Логирование
logging.basicConfig(level=logging.INFO)

# Словарь для хранения языка каждого пользователя
user_languages = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(f"Привет, {message.from_user.first_name}!\n"
                        "Кидай мне текст, и я его переведу.\n"
                        "Для смены языка используй команду /lang.")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply("Отправь мне текст, и я переведу его автоматически.\n"
                        "Команда /lang позволяет сменить язык перевода.")

@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Русский", "Английский", "Немецкий"]
    keyboard.add(*buttons)
    await message.reply("Выбери язык, на который хочешь переводить:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["Русский", "Английский", "Немецкий"])
async def set_user_language(message: types.Message):
    lang_map = {"Русский": "ru", "Английский": "en", "Немецкий": "de"}
    user_languages[message.from_user.id] = lang_map[message.text]
    await message.reply(f"Теперь я буду переводить на {message.text}.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler()
async def translate_text(message: types.Message):
    text = message.text
    if not text:
        return

    lang_detected = translator.detect(text).lang
    target_lang = user_languages.get(message.from_user.id, "en")  # По умолчанию английский

    if lang_detected == target_lang:  # Если текст уже на нужном языке, не переводим
        await message.reply("Текст уже на этом языке.")
        return

    translated_text = translator.translate(text, dest=target_lang).text
    await message.reply(f"Перевод:\n{translated_text}")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


    await bot.answer_inline_query(query.id, results)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
