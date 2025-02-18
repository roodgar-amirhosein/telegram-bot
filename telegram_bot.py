import os
import django
from asgiref.sync import sync_to_async
from openai import OpenAI

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
django.setup()

from main.models import ChatMessage
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

BOT_TOKEN = ""

client = OpenAI(
    api_key='',
)


# Use sync_to_async for database operations to make them compatible with async functions
@sync_to_async
def get_message_history(user_id):
    # Fetch only the necessary data from the database in a single query
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
    # Use bulk update to remove history more efficiently
    ChatMessage.objects.filter(user_id=user_id, active_memory=True).update(active_memory=False)


async def start(update: Update, context: CallbackContext):
    # Create a custom keyboard with a "Remove History" button
    keyboard = [
        [KeyboardButton("Remove History")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Hello! Send me a message.", reply_markup=reply_markup)


async def get_openai_response(user_message: str, user_id):
    try:
        conversation_history = await get_message_history(user_id)

        # Append the new user message to the history
        conversation_history.append({"role": "user", "content": user_message})

        # Make a request to OpenAI's 4o-mini model
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="gpt-4o-mini",
        )
        assistant_reply = chat_completion.choices[0].message.content

        # Append the assistant's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_message(update: Update, context: CallbackContext):
    try:
        user_id = update.message.chat_id
        text = update.message.text

        # Check if the message is "Remove History"
        if text.lower() == "remove history":
            # Remove message history from the database
            await remove_message_history(user_id)

            # Notify the user that history has been removed
            await update.message.reply_text("Your message history has been removed.")
            return  # Stop further processing for this message

        # Get OpenAI response for the user's message
        openai_response = await get_openai_response(text, user_id)

        # Save the user message and OpenAI response to the database
        await sync_to_async(ChatMessage.objects.create)(user_id=user_id, message=text, response=openai_response)

        # Send the OpenAI response to the user
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
