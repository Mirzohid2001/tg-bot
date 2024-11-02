# bot/handlers/methods_manuals.py

import os
import requests
from telegram import Update, InputFile
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler
from bot.utilities import (
    get_text,
    methods_menu_markup,
    back_button_markup,
)
from bot.handlers.main_menu import show_main_menu
from bot.constants import METHODS_MENU, METHOD_DETAILS
from bot.config import BACKEND_URL

async def handle_methods_manuals_entry(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    language = context.user_data.get('language', 'en')

    # Fetch methods from backend directly, without checking subscription
    response = requests.get(f'{BACKEND_URL}method/')
    if response.status_code == 200:
        methods_list = response.json()
        if methods_list:
            await update.callback_query.message.edit_text(get_text(context, 'choose_method'), reply_markup=methods_menu_markup(context, methods_list))
            return METHODS_MENU
        else:
            if language == 'en':
                text = "No methods available at the moment."
            else:
                text = "Методики в данный момент недоступны."
            await update.callback_query.message.edit_text(text, reply_markup=back_button_markup('back_to_main', context))
            return ConversationHandler.END
    else:
        if language == 'en':
            text = "❌ Error fetching methods."
        else:
            text = "❌ Ошибка при получении методик."
        await update.callback_query.message.edit_text(text, reply_markup=back_button_markup('back_to_main', context))
        return ConversationHandler.END

async def methods_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END
    elif data.startswith('method_'):
        method_id = data.replace('method_', '')
        await show_method_details(update, context, method_id)
        return METHOD_DETAILS

async def show_method_details(update: Update, context: CallbackContext, method_id):
    # Fetch method details from backend
    response = requests.get(f'{BACKEND_URL}method/{method_id}/')
    language = context.user_data.get('language', 'en')
    if response.status_code == 200:
        method_details = response.json()
        description = method_details.get('description', 'No description available.')
        if language == 'en':
            download_text = "📥 Download"
            back_text = "🔙 Back"
        else:
            download_text = "📥 Скачать"
            back_text = "🔙 Назад"
        keyboard = [
            [InlineKeyboardButton(download_text, callback_data=f'download_{method_id}')],
            [InlineKeyboardButton(back_text, callback_data='back_to_methods_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.edit_text(description, reply_markup=reply_markup)
    else:
        if language == 'en':
            text = "❌ Error fetching method details."
        else:
            text = "❌ Ошибка при получении деталей методики."
        await update.callback_query.message.edit_text(text, reply_markup=back_button_markup('back_to_methods_menu', context))

async def method_details_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith('download_'):
        method_id = data.replace('download_', '')
        await send_method_document(update, context, method_id)
        return METHOD_DETAILS
    elif data == 'back_to_methods_menu':
        # Fetch methods again
        response = requests.get(f'{BACKEND_URL}method/')
        if response.status_code == 200:
            methods_list = response.json()
            await query.message.edit_text(get_text(context, 'choose_method'), reply_markup=methods_menu_markup(context, methods_list))
            return METHODS_MENU
        else:
            language = context.user_data.get('language', 'en')
            if language == 'en':
                text = "❌ Error fetching methods."
            else:
                text = "❌ Ошибка при получении методик."
            await query.message.edit_text(text, reply_markup=back_button_markup('back_to_main', context))
            return ConversationHandler.END
    elif data == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END

async def send_method_document(update: Update, context: CallbackContext, method_id):
    # Fetch method file URL from backend
    response = requests.get(f'{BACKEND_URL}method/{method_id}/download/')
    if response.status_code == 200:
        file_info = response.json()
        file_url = file_info.get('file_url')
        if file_url:
            # Download the file and send it to the user
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                file_name = f"method_{method_id}.pdf"
                with open(file_name, 'wb') as f:
                    f.write(file_response.content)
                await update.callback_query.message.reply_document(InputFile(file_name))
                os.remove(file_name)  # Clean up the file after sending
            else:
                language = context.user_data.get('language', 'en')
                if language == 'en':
                    text = "❌ Error downloading the file."
                else:
                    text = "❌ Ошибка при загрузке файла."
                await update.callback_query.message.reply_text(text)
        else:
            language = context.user_data.get('language', 'en')
            if language == 'en':
                text = "❌ File URL not found."
            else:
                text = "❌ URL файла не найден."
            await update.callback_query.message.reply_text(text)
    else:
        language = context.user_data.get('language', 'en')
        if language == 'en':
            text = "❌ Error fetching method file."
        else:
            text = "❌ Ошибка при получении файла методики."
        await update.callback_query.message.reply_text(text)
