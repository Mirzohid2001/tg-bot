# bot/handlers/feedback.py

import requests
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters
from bot.utilities import get_text, back_button_markup
from bot.handlers.main_menu import show_main_menu
from bot.constants import FEEDBACK_MESSAGE
from bot.config import BACKEND_URL


async def handle_feedback_entry(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "📝 Please write your feedback:"
    else:
        text = "📝 Пожалуйста, напишите ваш отзыв:"
    await update.callback_query.message.edit_text(text,
                                                  reply_markup=back_button_markup('back_to_main', context))
    return FEEDBACK_MESSAGE


async def handle_feedback_message(update: Update, context: CallbackContext):
    feedback = update.message.text
    user_id = update.effective_chat.id
    language = context.user_data.get('language', 'en')

    try:
        response = requests.post(f'{BACKEND_URL}feedback/', json={"user_id": user_id, "message": feedback})
        if response.status_code == 201:
            if language == 'en':
                text = "✅ Thank you for your feedback!"
            else:
                text = "✅ Спасибо за ваш отзыв!"
            await update.message.reply_text(text)
            await show_main_menu(update, context)
        else:
            await update.message.reply_text(f"❌ Error submitting feedback. Response code: {response.status_code}")
            await show_main_menu(update, context)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error connecting to the server: {e}")
        await show_main_menu(update, context)
    return ConversationHandler.END
