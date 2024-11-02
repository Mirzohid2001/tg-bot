import os
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.helpers import escape_markdown

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)

# Replace with your actual bot token
TELEGRAM_BOT_TOKEN = '7901466690:AAFtUArAc1ELvSbdDL53SlgnZ1mUIPvHRgQ'

# Backend URL
BACKEND_URL = 'http://127.0.0.1:8000/subscription/'  # Replace with your backend URL

# Initialize the application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Conversation states
(
    LANGUAGE_SELECTION,
    BUY_SUBSCRIPTION_EMAIL,
    BUY_SUBSCRIPTION_PLAN,
    BUY_SUBSCRIPTION_PAYMENT_METHOD,
    BUY_SUBSCRIPTION_PAYMENT_DETAILS,
    GIFT_SUBSCRIPTION_CONTACT,
    GIFT_SUBSCRIPTION_PLAN,
    GIFT_SUBSCRIPTION_PAYMENT_METHOD,
    GIFT_SUBSCRIPTION_PAYMENT_DETAILS,
    FEEDBACK_MESSAGE,
    METHODS_MENU,
    METHOD_DETAILS,
    SUPPORT_MENU,
    SAVE_CARD,
    SAVE_CARD_EXPIRY,
    SAVE_CARD_NUMBER

) = range(16)

# Language texts
LANGUAGES = {
    'en': {
        'welcome': "Welcome!",
        'choose_language': "Please select your language:",
        'start_over': "To start over, send the /start command.",
        'help_text': (
            "🆘 *Help*:\n"
            "/start - Restart the bot\n"
            "/help - Help\n"
            "Bot features:\n"
            "• Purchase a subscription\n"
            "• Gift a subscription\n"
            "• Methods and manuals\n"
            "• About the product\n"
            "• Support\n"
            "• Statistics\n"
            "• View profile\n"
            "• Leave feedback"
        ),
        'register_success': "You have successfully registered! 🎉",
        'register_already': "You are already registered! ✔️",
        'register_error': "An error occurred during registration. ❌",
        'agreement_text': (
            "*User Agreement*:\n"
            "1. Your data will be used in accordance with our privacy policy.\n"
            "2. You are obliged to use our service legally and without violating the rights of other users.\n\n"
            "*Privacy Policy*:\n"
            "1. We collect and process your personal data to provide quality service.\n"
            "2. Your data will not be shared with third parties without your consent."
        ),
        'consent_prompt': "Please confirm your agreement with the terms of use and privacy policy.",
        'consent_received': "✅ Your consent has been received!",
        'no_subscription': "❌ You don't have an active subscription. Please purchase a subscription first.",
        'choose_method': "📚 Please choose one of the methods and manuals:",
    },
    'ru': {
        'welcome': "Добро пожаловать!",
        'choose_language': "Пожалуйста, выберите ваш язык:",
        'start_over': "Чтобы начать сначала, отправьте команду /start.",
        'help_text': (
            "🆘 *Помощь*:\n"
            "/start - Перезапустить бота\n"
            "/help - Помощь\n"
            "Возможности бота:\n"
            "• Купить подписку\n"
            "• Подарить подписку\n"
            "• Методики и руководства\n"
            "• Информация о продукте\n"
            "• Поддержка\n"
            "• Статистика\n"
            "• Просмотр профиля\n"
            "• Оставить отзыв"
        ),
        'register_success': "Вы успешно зарегистрированы! 🎉",
        'register_already': "Вы уже зарегистрированы! ✔️",
        'register_error': "Произошла ошибка при регистрации. ❌",
        'agreement_text': (
            "*Пользовательское соглашение*:\n"
            "1. Ваши данные будут использоваться в соответствии с нашей политикой конфиденциальности.\n"
            "2. Вы обязаны использовать наш сервис законно и не нарушать права других пользователей.\n\n"
            "*Политика конфиденциальности*:\n"
            "1. Мы собираем и обрабатываем ваши персональные данные для предоставления качественных услуг.\n"
            "2. Ваши данные не будут переданы третьим лицам без вашего согласия."
        ),
        'consent_prompt': "Пожалуйста, подтвердите ваше согласие с условиями использования и политикой конфиденциальности.",
        'consent_received': "✅ Ваше согласие получено!",
        'no_subscription': "❌ У вас нет активной подписки. Пожалуйста, сначала приобретите подписку.",
        'choose_method': "📚 Пожалуйста, выберите одну из методик и руководств:",
    }
}

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

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    username = update.effective_user.username or ''
    registration_status = register_user(user_id, username, context)

    # Get user language
    language = get_user_language(user_id)
    context.user_data['language'] = language

    # Check if user has given consent
    consent_given = check_user_consent(user_id)

    if consent_given:
        await show_main_menu(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='en')],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data='ru')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_text(context, 'choose_language'), reply_markup=reply_markup)
        return LANGUAGE_SELECTION

async def language_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    language = query.data
    context.user_data['language'] = language
    user_id = update.effective_chat.id
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
    await update.callback_query.message.reply_text(agreement_text, parse_mode='Markdown')
    await update.callback_query.message.reply_text(
        get_text(context, 'consent_prompt'),
        reply_markup=reply_markup)
    return ConversationHandler.END

async def consent_callback(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
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

async def show_main_menu(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'en')
    main_menu_text = "Main Menu:" if language == 'en' else "Главное меню:"
    if update.callback_query:
        await update.callback_query.message.reply_text(main_menu_text, reply_markup=main_menu_markup(context))
    else:
        await update.message.reply_text(main_menu_text, reply_markup=main_menu_markup(context))

async def main_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    message = query.data
    if message == 'buy_subscription':
        return await handle_buy_subscription_entry(update, context)
    elif message == 'gift_subscription':
        return await handle_gift_subscription_entry(update, context)
    elif message == 'methods_manuals':
        return await handle_methods_manuals_entry(update, context)
    elif message == 'about_product':
        await handle_about_product(update, context)
    elif message == 'statistics':
        await handle_statistics(update, context)
    elif message == 'profile':
        await handle_profile(update, context)
    elif message == 'feedback':
        return await handle_feedback_entry(update, context)
    elif message == 'support':
        return await handle_support(update, context)
    elif message == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END

def back_button_markup(callback_data, context):
    language = context.user_data.get('language', 'en')
    back_text = "🔙 Back" if language == 'en' else "🔙 Назад"
    keyboard = [
        [InlineKeyboardButton(back_text, callback_data=callback_data)],
    ]
    return InlineKeyboardMarkup(keyboard)

async def help_command(update: Update, context: CallbackContext):
    help_text = get_text(context, 'help_text')
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Subscription purchase conversation
async def handle_buy_subscription_entry(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "✉️ Please enter your email to receive the receipt:"
    else:
        text = "✉️ Пожалуйста, введите ваш email для получения чека:"
    await update.callback_query.message.edit_text(text,
                                                  reply_markup=back_button_markup('back_to_main', context))
    return BUY_SUBSCRIPTION_EMAIL

async def handle_buy_subscription_email(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = f"Your email {email} has been saved.\n\n**Step 1/3: Choose a subscription plan:**"
    else:
        text = f"Ваш email {email} сохранен.\n\n**Шаг 1/3: Выберите план подписки:**"
    await update.message.reply_text(text,
                                    reply_markup=subscription_plan_markup(context), parse_mode='Markdown')
    return BUY_SUBSCRIPTION_PLAN

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

async def handle_buy_subscription_plan(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    plan = query.data
    language = context.user_data.get('language', 'en')
    if plan == 'back_to_email':
        if language == 'en':
            text = "✉️ Please enter your email to receive the receipt:"
        else:
            text = "✉️ Пожалуйста, введите ваш email для получения чека:"
        await query.message.edit_text(text,
                                      reply_markup=back_button_markup('back_to_main', context))
        return BUY_SUBSCRIPTION_EMAIL
    elif plan == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END
    context.user_data['plan'] = plan
    # Ask for payment method
    if language == 'en':
        text = "**Step 2/3: Choose a payment method:**"
    else:
        text = "**Шаг 2/3: Выберите способ оплаты:**"
    await query.message.edit_text(text, reply_markup=payment_method_markup(context), parse_mode='Markdown')
    return BUY_SUBSCRIPTION_PAYMENT_METHOD

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

async def handle_buy_subscription_payment_method(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    payment_method = query.data
    language = context.user_data.get('language', 'en')
    if payment_method == 'back_to_plan':
        # Go back to plan selection
        if language == 'en':
            text = f"**Step 1/3: Choose a subscription plan:**"
        else:
            text = f"**Шаг 1/3: Выберите план подписки:**"
        await query.message.edit_text(text, reply_markup=subscription_plan_markup(context), parse_mode='Markdown')
        return BUY_SUBSCRIPTION_PLAN
    elif payment_method == 'pay_card':
        context.user_data['payment_method'] = 'card'
        # Proceed to payment details
        if language == 'en':
            text = "💳 Please enter your card number:"
        else:
            text = "💳 Пожалуйста, введите номер вашей карты:"
        await query.message.edit_text(text, reply_markup=back_button_markup('back_to_payment_method', context))
        return BUY_SUBSCRIPTION_PAYMENT_DETAILS

async def handle_buy_subscription_payment_details(update: Update, context: CallbackContext):
    card_number = update.message.text
    context.user_data['card_number'] = card_number
    # Process payment
    await process_payment(update, context)
    await show_main_menu(update, context)
    return ConversationHandler.END

async def process_payment(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    plan = context.user_data['plan']
    email = context.user_data['email']
    payment_method = context.user_data.get('payment_method', 'card')
    card_number = context.user_data.get('card_number', None)
    language = context.user_data.get('language', 'en')

    # Map plan names to backend values
    plan_mapping = {
        "monthly_subscription": "monthly",
        "yearly_subscription": "yearly"
    }
    plan_value = plan_mapping.get(plan, "")

    # Get subscription price
    price_response = requests.get(f'{BACKEND_URL}plan-price/{plan_value}/')
    if price_response.status_code == 200:
        price_info = price_response.json()
        amount = price_info.get('price', '0.00')
    else:
        amount = '0.00'

    payment_data = {
        "user_id": user_id,
        "plan": plan_value,
        "email": email,
        "amount": amount,
        "payment_method": payment_method,
        "card_number": card_number,
        "transaction_id": None  # Assuming no transaction ID in this example
    }

    # Process payment (Assuming payment is always successful in this example)
    try:
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            if language == 'en':
                text_success = "✅ Payment was successful."
                text_subscription = "✅ Subscription has been activated."
            else:
                text_success = "✅ Оплата успешно выполнена."
                text_subscription = "✅ Подписка активирована."
            await update.message.reply_text(text_success)
            # Activate subscription
            subscription_response = requests.post(f'{BACKEND_URL}subscription/', json={
                "user_id": user_id,
                "plan": plan_value,
                "email": email
            })
            if subscription_response.status_code == 201:
                await update.message.reply_text(text_subscription)
            else:
                await update.message.reply_text(
                    f"❌ Error activating subscription. Response code: {subscription_response.status_code}")
        else:
            await update.message.reply_text(f"❌ Error during payment. Response code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error connecting to the server: {e}")

# Gift Subscription conversation
async def handle_gift_subscription_entry(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "🎁 Please enter the recipient's contact (username or phone number):"
    else:
        text = "🎁 Пожалуйста, введите контакт получателя (имя пользователя или номер телефона):"
    await update.callback_query.message.edit_text(text,
                                                  reply_markup=back_button_markup('back_to_main', context))
    return GIFT_SUBSCRIPTION_CONTACT

async def handle_gift_subscription_contact(update: Update, context: CallbackContext):
    recipient_contact = update.message.text
    context.user_data['recipient_contact'] = recipient_contact
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = f"Recipient contact {recipient_contact} saved.\n\n**Step 1/3: Choose a subscription plan to gift:**"
    else:
        text = f"Контакт получателя {recipient_contact} сохранен.\n\n**Шаг 1/3: Выберите план подписки для подарка:**"
    await update.message.reply_text(text,
                                    reply_markup=subscription_plan_markup(context), parse_mode='Markdown')
    return GIFT_SUBSCRIPTION_PLAN

async def handle_gift_subscription_plan(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    plan = query.data
    language = context.user_data.get('language', 'en')
    if plan == 'back_to_contact':
        if language == 'en':
            text = "🎁 Please enter the recipient's contact (username or phone number):"
        else:
            text = "🎁 Пожалуйста, введите контакт получателя (имя пользователя или номер телефона):"
        await query.message.edit_text(text,
                                      reply_markup=back_button_markup('back_to_main', context))
        return GIFT_SUBSCRIPTION_CONTACT
    elif plan == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END
    context.user_data['plan'] = plan
    # Ask for payment method
    if language == 'en':
        text = "**Step 2/3: Choose a payment method:**"
    else:
        text = "**Шаг 2/3: Выберите способ оплаты:**"
    await query.message.edit_text(text, reply_markup=payment_method_markup(context), parse_mode='Markdown')
    return GIFT_SUBSCRIPTION_PAYMENT_METHOD

async def handle_gift_subscription_payment_method(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    payment_method = query.data
    language = context.user_data.get('language', 'en')
    if payment_method == 'back_to_plan':
        # Go back to plan selection
        if language == 'en':
            text = f"**Step 1/3: Choose a subscription plan to gift:**"
        else:
            text = f"**Шаг 1/3: Выберите план подписки для подарка:**"
        await query.message.edit_text(text, reply_markup=subscription_plan_markup(context), parse_mode='Markdown')
        return GIFT_SUBSCRIPTION_PLAN
    elif payment_method == 'pay_card':
        context.user_data['payment_method'] = 'card'
        # Proceed to payment details
        if language == 'en':
            text = "💳 Please enter your card number:"
        else:
            text = "💳 Пожалуйста, введите номер вашей карты:"
        await query.message.edit_text(text, reply_markup=back_button_markup('back_to_payment_method', context))
        return GIFT_SUBSCRIPTION_PAYMENT_DETAILS

async def handle_gift_subscription_payment_details(update: Update, context: CallbackContext):
    card_number = update.message.text
    context.user_data['card_number'] = card_number
    # Process gift payment
    await process_gift_payment(update, context)
    await show_main_menu(update, context)
    return ConversationHandler.END

async def process_gift_payment(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    plan = context.user_data['plan']
    recipient_contact = context.user_data['recipient_contact']
    payment_method = context.user_data.get('payment_method', 'card')
    card_number = context.user_data.get('card_number', None)
    language = context.user_data.get('language', 'en')

    # Map plan names to backend values
    plan_mapping = {
        "monthly_subscription": "monthly",
        "yearly_subscription": "yearly"
    }
    plan_value = plan_mapping.get(plan, "")

    # Get subscription price
    price_response = requests.get(f'{BACKEND_URL}plan-price/{plan_value}/')
    if price_response.status_code == 200:
        price_info = price_response.json()
        amount = price_info.get('price', '0.00')
    else:
        amount = '0.00'

    payment_data = {
        "user_id": user_id,
        "plan": plan_value,
        "amount": amount,
        "payment_method": payment_method,
        "card_number": card_number,
        "transaction_id": None  # Assuming no transaction ID in this example
    }

    # Process payment (Assuming payment is always successful in this example)
    try:
        # Use the existing /payment/ endpoint
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            if language == 'en':
                text_success = "✅ Payment was successful."
                text_gift = "✅ Subscription has been gifted."
            else:
                text_success = "✅ Оплата успешно выполнена."
                text_gift = "✅ Подписка подарена."
            await update.message.reply_text(text_success)
            # Activate subscription for recipient
            gift_response = requests.post(f'{BACKEND_URL}gift-subscription/', json={
                "user_id": user_id,
                "recipient_contact": recipient_contact,
                "plan": plan_value
            })
            if gift_response.status_code == 201:
                await update.message.reply_text(text_gift)
            else:
                await update.message.reply_text(
                    f"❌ Error gifting subscription. Response code: {gift_response.status_code}")
        else:
            await update.message.reply_text(f"❌ Error during payment. Response code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error connecting to the server: {e}")

# Methods and manuals menu
def check_user_subscription(user_id):
    response = requests.get(f'{BACKEND_URL}user-subscription/{user_id}/')
    if response.status_code == 200:
        subscription_info = response.json()
        is_active = subscription_info.get('is_active', False)
        return is_active
    else:
        return False

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

# Feedback conversation
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

# Show profile
def save_card_data(user_id, card_number, expiry_date):
    try:
        response = requests.post(f'{BACKEND_URL}save-card/', json={
            "user_id": user_id,
            "card_number": card_number,
            "expiry_date": expiry_date
        })
        return response.status_code == 201
    except requests.exceptions.RequestException as e:
        print(f"Error saving card: {e}")
        return False

# Karta ma'lumotlarini saqlash jarayonini boshlash
async def handle_save_card(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "💳 Please enter your card number:"
    else:
        text = "💳 Пожалуйста, введите номер вашей карты:"
    await update.callback_query.message.reply_text(text)
    return SAVE_CARD_NUMBER

# Karta raqamini olish
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

# Karta amal qilish muddatini olish va saqlash
async def save_card_expiry(update: Update, context: CallbackContext):
    expiry_date = update.message.text
    user_id = update.effective_chat.id
    card_number = context.user_data['card_number']

    # Backendga ma'lumotlarni yuborish
    if save_card_data(user_id, card_number, expiry_date):
        await update.message.reply_text("✅ Card saved successfully.")
    else:
        await update.message.reply_text("❌ Error saving card.")
    await show_main_menu(update, context)
    return ConversationHandler.END


async def handle_profile(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    response = requests.get(f'{BACKEND_URL}user-profile/{user_id}/')
    language = context.user_data.get('language', 'en')
    if response.status_code == 200:
        profile = response.json()
        card_info = profile.get('card', {})
        if card_info:
            card_text = get_text(context, 'profile_card_info').format(
                card_number=card_info.get('card_number', 'N/A'),
                expiry_date=card_info.get('expiry_date', 'N/A')
            )
        else:
            card_text = "No saved card." if language == 'en' else "Сохраненных карт нет."

        text = f"👤 *Profile*:\n{card_text}"
        await update.callback_query.message.edit_text(
            text,
            parse_mode='Markdown',
            reply_markup=back_button_markup('back_to_main', context)
        )
    else:
        await update.callback_query.message.edit_text("❌ Error retrieving profile information.")

save_card_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_save_card, pattern='^save_card$')],
    states={
        SAVE_CARD_NUMBER: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), save_card_number)
        ],
        SAVE_CARD_EXPIRY: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), save_card_expiry)
        ],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
)



# Support conversation
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

# Show statistics
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

# About product
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

# Conversation handlers
language_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANGUAGE_SELECTION: [CallbackQueryHandler(language_selection)],
    },
    fallbacks=[],
)

buy_subscription_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_buy_subscription_entry, pattern='^buy_subscription$')],
    states={
        BUY_SUBSCRIPTION_EMAIL: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_email),
            CallbackQueryHandler(handle_buy_subscription_entry, pattern='^back_to_main$'),
        ],
        BUY_SUBSCRIPTION_PLAN: [
            CallbackQueryHandler(handle_buy_subscription_plan,
                                 pattern='^(monthly_subscription|yearly_subscription|back_to_email|back_to_main)$')
        ],
        BUY_SUBSCRIPTION_PAYMENT_METHOD: [
            CallbackQueryHandler(handle_buy_subscription_payment_method,
                                 pattern='^(pay_card|back_to_plan)$')
        ],
        BUY_SUBSCRIPTION_PAYMENT_DETAILS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_payment_details),
            CallbackQueryHandler(handle_buy_subscription_payment_method, pattern='^back_to_payment_method$'),
        ],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
    per_message=False,
)

gift_subscription_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_gift_subscription_entry, pattern='^gift_subscription$')],
    states={
        GIFT_SUBSCRIPTION_CONTACT: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_gift_subscription_contact),
            CallbackQueryHandler(handle_gift_subscription_entry, pattern='^back_to_main$'),
        ],
        GIFT_SUBSCRIPTION_PLAN: [
            CallbackQueryHandler(handle_gift_subscription_plan,
                                 pattern='^(monthly_subscription|yearly_subscription|back_to_contact|back_to_main)$')
        ],
        GIFT_SUBSCRIPTION_PAYMENT_METHOD: [
            CallbackQueryHandler(handle_gift_subscription_payment_method,
                                 pattern='^(pay_card|back_to_plan)$')
        ],
        GIFT_SUBSCRIPTION_PAYMENT_DETAILS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_gift_subscription_payment_details),
            CallbackQueryHandler(handle_gift_subscription_payment_method, pattern='^back_to_payment_method$'),
        ],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
    per_message=False,
)

methods_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_methods_manuals_entry, pattern='^methods_manuals$')],
    states={
        METHODS_MENU: [CallbackQueryHandler(methods_menu_handler)],
        METHOD_DETAILS: [CallbackQueryHandler(method_details_handler)],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
    per_message=False,
)

feedback_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_feedback_entry, pattern='^feedback$')],
    states={
        FEEDBACK_MESSAGE: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_feedback_message),
            CallbackQueryHandler(handle_feedback_entry, pattern='^back_to_main$'),
        ],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
    per_message=False,
)

support_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_support, pattern='^support$')],
    states={
        SUPPORT_MENU: [CallbackQueryHandler(support_menu_handler)],
    },
    fallbacks=[CallbackQueryHandler(main_menu_handler, pattern='^back_to_main$')],
    per_message=False,
)

# Add handlers to the application
application.add_handler(language_conv_handler)
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CallbackQueryHandler(consent_callback, pattern='^consent_given$'))
application.add_handler(CallbackQueryHandler(main_menu_handler,
                                             pattern='^(about_product|statistics|profile|back_to_main)$'))
application.add_handler(buy_subscription_conv_handler)
application.add_handler(gift_subscription_conv_handler)
application.add_handler(methods_conv_handler)
application.add_handler(feedback_conv_handler)
application.add_handler(support_conv_handler)

if __name__ == '__main__':
    application.run_polling()
