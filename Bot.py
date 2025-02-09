import logging
import asyncio
from uuid import uuid4
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from googletrans import Translator

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
translator = Translator()

# Логирование
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(f"Привет, {message.from_user.first_name}! "
                        "Просто отправь текст, и я переведу его!")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply("Отправь мне текст, и я переведу его автоматически.")

@dp.message_handler()
async def translate_text(message: types.Message):
    text = message.text
    if not text:
        return

    # Определение языка
    lang_detected = translator.detect(text).lang
    target_lang = 'en' if lang_detected == 'ru' else 'ru'

    translated_text = translator.translate(text, dest=target_lang).text
    await message.reply(f"Перевод:\n{translated_text}")

@dp.message_handler(content_types=['photo'])
async def handle_image(message: types.Message):
    caption = message.caption
    if not caption:
        await bot.send_photo(message.chat.id, message.photo[-1].file_id,
                             caption="Нет подписи для перевода.")
        return

    lang_detected = translator.detect(caption).lang
    target_lang = 'en' if lang_detected == 'ru' else 'ru'
    translated_text = translator.translate(caption, dest=target_lang).text

    await bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=translated_text)

@dp.inline_handler(lambda query: query.query.strip() != "")
async def inline_query(query: types.InlineQuery):
    text = query.query.strip()
    lang_detected = translator.detect(text).lang
    target_lang = 'en' if lang_detected == 'ru' else 'ru'

    translated_text = translator.translate(text, dest=target_lang).text
    results = [types.InlineQueryResultArticle(
        id=str(uuid4()), title=translated_text,
        input_message_content=types.InputTextMessageContent(message_text=translated_text)
    )]

    await bot.answer_inline_query(query.id, results)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
