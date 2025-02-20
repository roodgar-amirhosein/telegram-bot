import asyncio
import os
import django
from asgiref.sync import sync_to_async
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
django.setup()

from main.models import ChatMessage
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext


BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=OPENAI_API_KEY,
)


# Use sync_to_async for database operations to make them compatible with async functions
@sync_to_async
def get_message_history(user_id):
    last_messages = ChatMessage.objects.filter(user_id=user_id, active_memory=True).values("message", "response")
    conversation_history = [
        {"role": "user", "content": msg["message"]} for msg in last_messages
    ] + [
        {"role": "assistant", "content": msg["response"]} for msg in last_messages
    ]
    return conversation_history


# Use sync_to_async to remove message history
@sync_to_async
def remove_message_history(user_id):
    ChatMessage.objects.filter(user_id=user_id, active_memory=True).update(active_memory=False)


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Remove History")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("در چه زمینه ای میتونم کمکتون کنم", reply_markup=reply_markup)


async def get_openai_response(user_message: str, user_id):
    max_retries = 3
    start_prompt = {"role": "system", "content": "تو یه دستیاری به سوالات جواب بده"}
    for attempt in range(max_retries):
        try:
            conversation_history = await get_message_history(user_id)
            conversation_history.append(start_prompt)  # Add the start prompt
            conversation_history.append({"role": "user", "content": user_message})

            chat_completion = client.chat.completions.create(
                messages=conversation_history,
                model="gpt-4o-mini",
            )
            return chat_completion.choices[0].message.content

        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait before retrying
            else:
                return f"Error: {str(e)}"


async def handle_message(update: Update, context: CallbackContext):
    try:
        user_id = update.message.chat_id
        text = update.message.text

        if text.lower() == "remove history":
            await remove_message_history(user_id)

            await update.message.reply_text("حافظه ی چت پاک شد!")
            return  # Stop further processing for this message

        openai_response = await get_openai_response(text, user_id)

        await sync_to_async(ChatMessage.objects.create)(user_id=user_id, message=text, response=openai_response)

        await update.message.reply_text(openai_response)
    except Exception as e:
        print(e)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
