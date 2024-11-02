# bot/handlers/save_card.py

import requests
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters
from bot.utilities import save_card_data, get_text
from bot.handlers.main_menu import show_main_menu
from bot.constants import SAVE_CARD_NUMBER, SAVE_CARD_EXPIRY
from bot.config import BACKEND_URL

async def handle_save_card(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "💳 Please enter your card number:"
    else:
        text = "💳 Пожалуйста, введите номер вашей карты:"
    await update.callback_query.message.reply_text(text)
    return SAVE_CARD_NUMBER

async def save_card_number(update: Update, context: CallbackContext):
    card_number = update.message.text
    context.user_data['card_number'] = card_number
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "💳 Enter card expiry date (MM/YY):"
    else:
        text = "💳 Введите срок действия карты (ММ/ГГ):"
    await update.message.reply_text(text)
    return SAVE_CARD_EXPIRY

async def save_card_expiry(update: Update, context: CallbackContext):
    expiry_date = update.message.text
    user_id = update.effective_chat.id
    card_number = context.user_data['card_number']

    # Send data to backend
    if save_card_data(user_id, card_number, expiry_date):
        await update.message.reply_text("✅ Card saved successfully.")
    else:
        await update.message.reply_text("❌ Error saving card.")
    await show_main_menu(update, context)
    return ConversationHandler.END
