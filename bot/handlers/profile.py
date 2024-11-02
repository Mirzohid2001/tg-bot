# bot/handlers/profile.py

import requests
from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from bot.utilities import get_text, back_button_markup
from bot.config import BACKEND_URL

async def handle_profile(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    response = requests.get(f'{BACKEND_URL}user-profile/{user_id}/')
    language = context.user_data.get('language', 'en')
    if response.status_code == 200:
        profile = response.json()

        # Получаем информацию о карте
        card_info = profile.get('card', {})
        if card_info:
            card_text = get_text(context, 'profile_card_info').format(
                card_number=escape_markdown(card_info.get('card_number', 'N/A'), version=2),
                expiry_date=escape_markdown(card_info.get('expiry_date', 'N/A'), version=2)
            )
        else:
            card_text = "No saved card." if language == 'en' else "Сохраненных карт нет."

        # Получаем информацию о подписке
        subscription_info = profile.get('subscription', {})
        if subscription_info:
            subscription_text = get_text(context, 'profile_subscription_info').format(
                plan=escape_markdown(subscription_info.get('plan', 'N/A'), version=2),
                expires_at=escape_markdown(subscription_info.get('expires_at', 'N/A'), version=2)
            )
        else:
            subscription_text = "No active subscription." if language == 'en' else "Нет активной подписки."

        # Собираем полный текст профиля и экранируем специальные символы
        text = escape_markdown(f"👤 *Profile*:\n\n{card_text}\n{subscription_text}", version=2)

        await update.callback_query.message.edit_text(
            text,
            parse_mode='MarkdownV2',
            reply_markup=back_button_markup('back_to_main', context)
        )
    else:
        await update.callback_query.message.edit_text("❌ Error retrieving profile information.")
