import openai
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from django.conf import settings

# Set API Keys
openai.api_key = settings.OPENAI_API_KEY
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN

# Logger
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Send me a message, and I'll reply using OpenAI.")

async def handle_message(update: Update, context: CallbackContext):
    from .models import ChatMessage
    user_id = update.message.chat_id
    user_text = update.message.text

    # Generate OpenAI response
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": user_text}]
    # )["choices"][0]["message"]["content"]
    response = 'sample response'

    # Save chat history to the database
    ChatMessage.objects.create(user_id=user_id, message=user_text, response=response)

    # Reply to user
    await update.message.reply_text(response)

async def clear_memory(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    # Clear AI memory (not deleting chat history)
    await update.message.reply_text("Memory cleared. Starting a fresh conversation.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_memory))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

