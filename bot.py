import asyncio
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Импорт конфигурации
from config import TOKEN, GROUPS, PROFANITY_FILE

async def profanity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений и проверка на мат."""
    message = update.message
    if message is None or message.chat.id not in GROUPS:
        return  # Игнорировать, если не в разрешенных группах

    text = message.text or message.caption or ""
    if not text:
        return

    # Загрузить set мата, если не загружен
    if not hasattr(profanity_handler, 'profanity_set'):
        with open(PROFANITY_FILE, 'r', encoding='utf-8') as f:
            profanity_list = json.load(f)
        profanity_handler.profanity_set = set(profanity_list)
        logging.info(f"Загружено {len(profanity_handler.profanity_set)} слов мата.")

    # Проверка на мат
    words = text.lower().split()
    if any(word in profanity_handler.profanity_set for word in words):
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            logging.info(f"Удалено сообщение с матом от {message.from_user.username} в {message.chat.title}")
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

def main():
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logging.error("Пожалуйста, укажите токен бота в config.py")
        return

    # Построение приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчика для текстовых сообщений и подписей
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, profanity_handler))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()