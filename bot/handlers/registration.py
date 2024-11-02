# bot/handlers/registration.py

import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from bot.config import BACKEND_URL
from bot.utilities import (
    get_text,
    save_user_language,
    register_user,
    check_user_consent,
    get_user_language,  # Добавлено
)
from bot.buttons import language_selection_keyboard
from bot.handlers.main_menu import show_main_menu
from bot.constants import LANGUAGE_SELECTION

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id  # Изменено
    username = update.effective_user.first_name or update.effective_user.username or ''
    registration_status = register_user(user_id, username, context)

    # Получаем язык пользователя
    language = get_user_language(user_id)
    context.user_data['language'] = language

    # Проверяем, давал ли пользователь согласие
    consent_given = check_user_consent(user_id)

    if consent_given:
        # Если пользователь уже зарегистрирован и дал согласие
        welcome_text = get_text(context, 'welcome_back').format(username=username)
        await update.message.reply_text(welcome_text)
        await show_main_menu(update, context)
    else:
        # Если пользователь новый, спрашиваем язык и показываем соглашение
        reply_markup = language_selection_keyboard()
        await update.message.reply_text(get_text(context, 'choose_language'), reply_markup=reply_markup)
        return LANGUAGE_SELECTION

async def language_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    language = query.data
    context.user_data['language'] = language
    user_id = update.effective_user.id  # Изменено
    username = update.effective_user.username or ''
    # Save user language
    save_user_language(user_id, language)
    registration_status = register_user(user_id, username, context)
    welcome_text = get_text(context, 'welcome')
    await query.edit_message_text(f"{welcome_text}\n\n{registration_status}")
    return await send_documents(update, context)

async def send_documents(update: Update, context: CallbackContext):
    agreement_text = get_text(context, 'agreement_text')
    consent_button_text = "✅ I Agree" if context.user_data['language'] == 'en' else "✅ Я согласен"
    keyboard = [[InlineKeyboardButton(consent_button_text, callback_data='consent_given')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Проверяем, откуда пришёл запрос
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    await message.reply_text(agreement_text, parse_mode='Markdown')
    await message.reply_text(
        get_text(context, 'consent_prompt'),
        reply_markup=reply_markup)
    return ConversationHandler.END

async def consent_callback(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_id = update.effective_user.id  # Изменено
    try:
        response = requests.post(f'{BACKEND_URL}consent/', json={"user_id": user_id, "consent_given": True})
        if response.status_code == 201:
            await update.callback_query.message.edit_text(get_text(context, 'consent_received'))
            await show_main_menu(update, context)
        else:
            await update.callback_query.message.edit_text(
                f"❌ Error registering consent. Response code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        await update.callback_query.message.edit_text(f"❌ Error connecting to the server: {e}")
