# bot/handlers/statistics.py

import requests
from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from bot.utilities import get_text, back_button_markup
from bot.config import BACKEND_URL

async def handle_statistics(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    response = requests.get(f'{BACKEND_URL}statistics/{user_id}/')
    language = context.user_data.get('language', 'en')
    if response.status_code == 200:
        stats = response.json()
        total_payments = stats.get('total_payments') or '0.00'
        subscription_count = stats.get('subscription_count') or '0'
        last_payment_date = stats.get('last_payment_date') or 'N/A'
        # Escape data
        total_payments = escape_markdown(str(total_payments), version=2)
        subscription_count = escape_markdown(str(subscription_count), version=2)
        last_payment_date = escape_markdown(str(last_payment_date), version=2)
        if language == 'en':
            text = (
                f"📊 *Statistics*:\n\nTotal payment amount: {total_payments}\n"
                f"Number of subscriptions: {subscription_count}\n"
                f"Last payment: {last_payment_date}"
            )
        else:
            text = (
                f"📊 *Статистика*:\n\nОбщая сумма платежей: {total_payments}\n"
                f"Количество подписок: {subscription_count}\n"
                f"Последний платеж: {last_payment_date}"
            )
        await update.callback_query.message.edit_text(
            text,
            parse_mode='MarkdownV2',
            reply_markup=back_button_markup('back_to_main', context)
        )
    elif response.status_code == 404:
        if language == 'en':
            text = "❌ Statistics are not available yet. You might not have made any payments yet."
        else:
            text = "❌ Статистика пока недоступна. Возможно, вы ещё не совершали платежей."
        await update.callback_query.message.edit_text(text)
    else:
        if language == 'en':
            text = f"❌ Error retrieving statistics. Response code: {response.status_code}"
        else:
            text = f"❌ Ошибка при получении статистики. Код ответа: {response.status_code}"
        await update.callback_query.message.edit_text(text)
