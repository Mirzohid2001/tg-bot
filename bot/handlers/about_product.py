# bot/handlers/about_product.py

import requests
from telegram import Update
from telegram.ext import CallbackContext
from bot.utilities import back_button_markup
from bot.config import BACKEND_URL

async def handle_about_product(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    response = requests.get(f'{BACKEND_URL}about/')
    language = context.user_data.get('language', 'en')
    if response.status_code == 200:
        product_info = response.json()
        if language == 'en':
            text = (
                f"🛍 *Name*: {product_info['name']}\n"
                f"💵 *Monthly Price*: {product_info['price_monthly']}\n"
                f"💳 *Yearly Price*: {product_info['price_yearly']}\n\n"
                f"{product_info['description']}"
            )
        else:
            text = (
                f"🛍 *Название*: {product_info['name']}\n"
                f"💵 *Цена за месяц*: {product_info['price_monthly']}\n"
                f"💳 *Цена за год*: {product_info['price_yearly']}\n\n"
                f"{product_info['description']}"
            )
        await update.callback_query.message.edit_text(text, parse_mode='Markdown',
                                                      reply_markup=back_button_markup('back_to_main', context))
    else:
        if language == 'en':
            text = f"❌ Error retrieving product information. Response code: {response.status_code}"
        else:
            text = f"❌ Ошибка при получении информации о продукте. Код ответа: {response.status_code}"
        await update.callback_query.message.edit_text(text)
