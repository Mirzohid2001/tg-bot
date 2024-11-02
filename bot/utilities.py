# bot/utilities.py

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import BACKEND_URL
from bot.language import LANGUAGES


def get_text(context, key):
    language = context.user_data.get('language', 'en')
    return LANGUAGES[language].get(key, '')


def register_user(user_id, username, context):
    response = requests.post(f'{BACKEND_URL}register/', json={"user_id": user_id, "username": username})
    if response.status_code == 201:
        return get_text(context, 'register_success')
    elif response.status_code == 200:
        return get_text(context, 'register_already')
    else:
        return get_text(context, 'register_error')


def check_user_consent(user_id):
    response = requests.get(f'{BACKEND_URL}consent/{user_id}/')
    if response.status_code == 200:
        consent_info = response.json()
        return consent_info.get('consent_given', False)
    else:
        return False


def get_user_language(user_id):
    response = requests.get(f'{BACKEND_URL}user-language/{user_id}/')
    if response.status_code == 200:
        user_info = response.json()
        return user_info.get('language', 'en')
    else:
        return 'en'


def save_user_language(user_id, language):
    requests.post(f'{BACKEND_URL}user-language/', json={"user_id": user_id, "language": language})


def back_button_markup(callback_data, context):
    language = context.user_data.get('language', 'en')
    back_text = "🔙 Back" if language == 'en' else "🔙 Назад"
    keyboard = [
        [InlineKeyboardButton(back_text, callback_data=callback_data)],
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_markup(context):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        keyboard = [
            [InlineKeyboardButton("💼 Purchase Subscription", callback_data='buy_subscription')],
            [InlineKeyboardButton("🎁 Gift a Subscription", callback_data='gift_subscription')],
            [InlineKeyboardButton("📚 Methods and Manuals", callback_data='methods_manuals')],
            [InlineKeyboardButton("ℹ️ About Product", callback_data='about_product')],
            [InlineKeyboardButton("💳 Save Card", callback_data='save_card')],
            [InlineKeyboardButton("🛠 Support", callback_data='support')],
            [InlineKeyboardButton("📊 My Statistics", callback_data='statistics')],
            [InlineKeyboardButton("👤 My Profile", callback_data='profile')],
            [InlineKeyboardButton("📩 Leave Feedback", callback_data='feedback')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("💼 Купить подписку", callback_data='buy_subscription')],
            [InlineKeyboardButton("🎁 Подарить подписку", callback_data='gift_subscription')],
            [InlineKeyboardButton("📚 Методики и руководства", callback_data='methods_manuals')],
            [InlineKeyboardButton("ℹ️ О продукте", callback_data='about_product')],
            [InlineKeyboardButton("💳 Сохранить карту", callback_data='save_card')],
            [InlineKeyboardButton("🛠 Поддержка", callback_data='support')],
            [InlineKeyboardButton("📊 Моя статистика", callback_data='statistics')],
            [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
            [InlineKeyboardButton("📩 Оставить отзыв", callback_data='feedback')],
        ]
    return InlineKeyboardMarkup(keyboard)


def subscription_plan_markup(context):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        keyboard = [
            [InlineKeyboardButton("📅 Monthly Subscription", callback_data='monthly_subscription')],
            [InlineKeyboardButton("📆 Yearly Subscription", callback_data='yearly_subscription')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_email')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📅 Месячная подписка", callback_data='monthly_subscription')],
            [InlineKeyboardButton("📆 Годовая подписка", callback_data='yearly_subscription')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_email')],
        ]
    return InlineKeyboardMarkup(keyboard)


def payment_method_markup(context):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        keyboard = [
            [InlineKeyboardButton("💳 Credit Card", callback_data='pay_card')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_plan')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("💳 Кредитная карта", callback_data='pay_card')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_plan')],
        ]
    return InlineKeyboardMarkup(keyboard)


def methods_menu_markup(context, methods_list):
    language = context.user_data.get('language', 'en')
    keyboard = []
    for method in methods_list:
        method_id = method.get('id')
        method_name = method.get('name')
        keyboard.append([InlineKeyboardButton(method_name, callback_data=f'method_{method_id}')])
    back_text = "🔙 Back" if language == 'en' else "🔙 Назад"
    keyboard.append([InlineKeyboardButton(back_text, callback_data='back_to_main')])
    return InlineKeyboardMarkup(keyboard)


def check_user_subscription(user_id):
    response = requests.get(f'{BACKEND_URL}user-subscription/{user_id}/')
    if response.status_code == 200:
        subscription_info = response.json()
        is_active = subscription_info.get('is_active', False)
        return is_active
    else:
        return False


def save_card_data(user_id, card_number, expiry_date):
    try:
        response = requests.post(f'{BACKEND_URL}save-card/', json={
            "user_id": user_id,
            "card_number": card_number,
            "expiry_date": expiry_date
        })
        if response.status_code == 201:
            return True
        else:
            print(f"Error saving card: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error saving card: {e}")
        return False