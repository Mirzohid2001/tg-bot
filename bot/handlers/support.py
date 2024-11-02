# bot/handlers/support.py

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from bot.utilities import get_text, back_button_markup
from bot.constants import SUPPORT_MENU
from bot.config import BACKEND_URL
from bot.handlers.main_menu import show_main_menu

async def handle_support(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "🛠 Please choose an option:"
        keyboard = [
            [InlineKeyboardButton("📞 Contact", callback_data='support_contact')],
            [InlineKeyboardButton("💡 Advice", callback_data='support_advice')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
    else:
        text = "🛠 Пожалуйста, выберите опцию:"
        keyboard = [
            [InlineKeyboardButton("📞 Контакт", callback_data='support_contact')],
            [InlineKeyboardButton("💡 Советы", callback_data='support_advice')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    return SUPPORT_MENU

async def support_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    choice = query.data
    language = context.user_data.get('language', 'en')
    if choice == 'support_contact':
        # Provide contact information
        response = requests.get(f'{BACKEND_URL}support/')
        if response.status_code == 200:
            support_info = response.json()
            email = support_info.get('email', 'N/A')
            phone = support_info.get('phone', 'N/A')
            working_hours = support_info.get('working_hours', 'N/A')
            if language == 'en':
                support_text = (
                    f"🛠 *Support Contact*:\n"
                    f"📧 Email: {email}\n"
                    f"📞 Phone: {phone}\n"
                    f"⏰ Working Hours: {working_hours}"
                )
            else:
                support_text = (
                    f"🛠 *Контактная информация*:\n"
                    f"📧 Email: {email}\n"
                    f"📞 Телефон: {phone}\n"
                    f"⏰ Часы работы: {working_hours}"
                )
            await query.message.edit_text(support_text, parse_mode='Markdown',
                                          reply_markup=back_button_markup('back_to_support', context))
        else:
            if language == 'en':
                text = f"❌ Error retrieving support information. Response code: {response.status_code}"
            else:
                text = f"❌ Ошибка при получении информации поддержки. Код ответа: {response.status_code}"
            await query.message.edit_text(text, reply_markup=back_button_markup('back_to_support', context))
        return SUPPORT_MENU  # Stay in support menu
    elif choice == 'support_advice':
        # Fetch advice from backend
        response = requests.get(f'{BACKEND_URL}advice/')
        if response.status_code == 200:
            advice_list = response.json()
            advice_text = ""
            if advice_list:
                for advice in advice_list:
                    title = advice.get('title', 'Advice')
                    content = advice.get('content', 'No advice available at the moment.')
                    advice_text += f"💡 *{title}*\n\n{content}\n\n"
            else:
                if language == 'en':
                    advice_text = "No advice available at the moment."
                else:
                    advice_text = "Советы в данный момент недоступны."
            await query.message.edit_text(advice_text.strip(), parse_mode='Markdown',
                                          reply_markup=back_button_markup('back_to_support', context))
        else:
            if language == 'en':
                text = f"❌ Error retrieving advice. Response code: {response.status_code}"
            else:
                text = f"❌ Ошибка при получении советов. Код ответа: {response.status_code}"
            await query.message.edit_text(text, reply_markup=back_button_markup('back_to_support', context))
        return SUPPORT_MENU  # Stay in support menu
    elif choice == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END
    elif choice == 'back_to_support':
        return await handle_support(update, context)
    else:
        # Unrecognized input
        return SUPPORT_MENU
