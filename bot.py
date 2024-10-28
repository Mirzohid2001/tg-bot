import requests
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Contact,
)
from telegram.helpers import escape_markdown

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackContext,
)

TELEGRAM_BOT_TOKEN = '7901466690:AAFtUArAc1ELvSbdDL53SlgnZ1mUIPvHRgQ'

BACKEND_URL = 'http://127.0.0.1:8000/subscription/'  # Backend URL

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Define conversation states
(
    BUY_SUBSCRIPTION_EMAIL,
    BUY_SUBSCRIPTION_PLAN,
    BUY_SUBSCRIPTION_PAYMENT_METHOD,
    BUY_SUBSCRIPTION_PAYMENT_DETAILS,
    GIFT_SUBSCRIPTION_CONTACT,
    GIFT_SUBSCRIPTION_PLAN,
    GIFT_SUBSCRIPTION_PAYMENT_METHOD,
    GIFT_SUBSCRIPTION_PAYMENT_DETAILS,
    FEEDBACK_MESSAGE,
) = range(9)


def register_user(user_id, username):
    response = requests.post(f'{BACKEND_URL}register/', json={"user_id": user_id, "username": username})
    if response.status_code == 201:
        return "Вы успешно зарегистрированы! 🎉"
    elif response.status_code == 200:
        return "Вы уже зарегистрированы! ✔️"
    else:
        return "Ошибка регистрации. ❌"


async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    username = update.message.chat.username or ''
    registration_status = register_user(user_id, username)

    keyboard = [[KeyboardButton("🚀 Начать")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f'{registration_status}', reply_markup=reply_markup)


async def send_documents(update: Update, context: CallbackContext):
    agreement_text = """
*Пользовательское соглашение*:
1. Ваши данные будут использоваться в соответствии с нашей политикой конфиденциальности.
2. Вы обязуетесь использовать наш сервис в соответствии с законодательством и не нарушать права других пользователей.

*Политика конфиденциальности*:
1. Мы собираем и обрабатываем ваши личные данные в целях предоставления качественного сервиса.
2. Ваши данные не будут переданы третьим лицам без вашего согласия.
    """

    await update.message.reply_text(agreement_text, parse_mode='Markdown')
    keyboard = [[KeyboardButton("✅ Согласен")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Подтвердите, что вы согласны с условиями использования и политикой конфиденциальности.",
        reply_markup=reply_markup)


async def consent_callback(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    try:
        response = requests.post(f'{BACKEND_URL}consent/', json={"user_id": user_id, "consent_given": True})
        if response.status_code == 201:
            await update.message.reply_text('✅ Согласие принято!', reply_markup=main_menu_markup())
        else:
            await update.message.reply_text(f'❌ Ошибка при регистрации согласия. Код ответа: {response.status_code}')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка соединения с сервером: {e}')


def main_menu_markup():
    keyboard = [
        [KeyboardButton("💼 Приобрести себе")],
        [KeyboardButton("🎁 Подарить подписку")],
        [KeyboardButton("ℹ️ О продукте")],
        [KeyboardButton("🛠 Поддержка")],
        [KeyboardButton("📊 Моя Статистика")],
        [KeyboardButton("👤 Мой Профиль")],
        [KeyboardButton("📩 Оставить отзыв")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def main_menu_handler(update: Update, context: CallbackContext):
    message = update.message.text
    if message == '💼 Приобрести себе':
        return await handle_buy_subscription_entry(update, context)
    elif message == '🎁 Подарить подписку':
        return await handle_gift_subscription_entry(update, context)
    elif message == 'ℹ️ О продукте':
        await handle_about_product(update, context)
    elif message == '🛠 Поддержка':
        await handle_support(update, context)
    elif message == '📊 Моя Статистика':
        await handle_statistics(update, context)
    elif message == '👤 Мой Профиль':
        await handle_profile(update, context)
    elif message == '📩 Оставить отзыв':
        return await handle_feedback_entry(update, context)


# Subscription purchase conversation
async def handle_buy_subscription_entry(update: Update, context: CallbackContext):
    await update.message.reply_text('✉️ Введите ваш email для получения чека:')
    return BUY_SUBSCRIPTION_EMAIL


async def handle_buy_subscription_email(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    await update.message.reply_text(f'Ваш email {email} сохранен. Выберите план подписки:',
                                    reply_markup=subscription_plan_markup())
    return BUY_SUBSCRIPTION_PLAN


def subscription_plan_markup():
    keyboard = [
        [KeyboardButton("📅 Месячная подписка")],
        [KeyboardButton("📆 Годовая подписка")],
        [KeyboardButton("🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def handle_buy_subscription_plan(update: Update, context: CallbackContext):
    plan = update.message.text
    if plan == '🔙 Назад':
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
        return ConversationHandler.END
    context.user_data['plan'] = plan
    await update.message.reply_text('Выберите метод оплаты:', reply_markup=payment_method_markup())
    return BUY_SUBSCRIPTION_PAYMENT_METHOD


def payment_method_markup():
    keyboard = [
        [KeyboardButton("💳 Картой")],
        [KeyboardButton("₿ Криптовалютой")],
        [KeyboardButton("🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def handle_buy_subscription_payment_method(update: Update, context: CallbackContext):
    payment_method = update.message.text
    if payment_method == '🔙 Назад':
        await update.message.reply_text('Выберите план подписки снова:', reply_markup=subscription_plan_markup())
        return BUY_SUBSCRIPTION_PLAN
    context.user_data['payment_method'] = payment_method
    if payment_method == '💳 Картой':
        await update.message.reply_text('Введите номер карты:')
    elif payment_method == '₿ Криптовалютой':
        await update.message.reply_text('Введите ваш крипто-адрес:')
    return BUY_SUBSCRIPTION_PAYMENT_DETAILS


async def handle_buy_subscription_payment_details(update: Update, context: CallbackContext):
    payment_method = context.user_data['payment_method']
    if payment_method == '💳 Картой':
        context.user_data['card_number'] = update.message.text
    elif payment_method == '₿ Криптовалютой':
        context.user_data['crypto_address'] = update.message.text
    await process_payment(update, context)
    await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
    return ConversationHandler.END


async def process_payment(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    plan = context.user_data['plan']
    email = context.user_data['email']
    payment_method = context.user_data['payment_method']

    # Map plan names to backend expected values
    plan_mapping = {
        "📅 Месячная подписка": "monthly",
        "📆 Годовая подписка": "yearly"
    }
    plan_value = plan_mapping.get(plan, "")

    payment_data = {
        "user_id": user_id,
        "plan": plan_value,
        "email": email,
        "payment_method": payment_method,
        "amount": "10.00" if plan_value == "monthly" else "100.00"  # Example amounts
    }

    if payment_method == '💳 Картой':
        payment_data["card_number"] = context.user_data['card_number']
    elif payment_method == '₿ Криптовалютой':
        payment_data["crypto_address"] = context.user_data['crypto_address']

    try:
        # First, make the payment
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            await update.message.reply_text('✅ Оплата успешно завершена.')
            # Then, activate the subscription
            subscription_response = requests.post(f'{BACKEND_URL}subscription/', json={
                "user_id": user_id,
                "plan": plan_value,
                "email": email
            })
            if subscription_response.status_code == 201:
                await update.message.reply_text('✅ Подписка активирована.')
            else:
                await update.message.reply_text(
                    f'❌ Ошибка при активации подписки. Код ответа: {subscription_response.status_code}')
        else:
            await update.message.reply_text(f'❌ Ошибка при оплате. Код ответа: {response.status_code}')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка соединения с сервером: {e}')


# Gift subscription conversation (Modified to accept contact)
async def handle_gift_subscription_entry(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Пожалуйста, отправьте контакт получателя:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Отправить контакт", request_contact=True)], [KeyboardButton("🔙 Назад")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return GIFT_SUBSCRIPTION_CONTACT


async def handle_gift_subscription_contact(update: Update, context: CallbackContext):
    if update.message.contact:
        recipient_contact = update.message.contact
        recipient_user_id = recipient_contact.user_id
        recipient_first_name = recipient_contact.first_name
        recipient_last_name = recipient_contact.last_name
        if recipient_user_id:
            context.user_data['recipient_user_id'] = recipient_user_id
            context.user_data['recipient_first_name'] = recipient_first_name
            context.user_data['recipient_last_name'] = recipient_last_name
            await update.message.reply_text('Выберите план подписки:', reply_markup=subscription_plan_markup())
            return GIFT_SUBSCRIPTION_PLAN
        else:
            await update.message.reply_text('Не удалось получить ID пользователя из контакта. Попробуйте еще раз.')
            return GIFT_SUBSCRIPTION_CONTACT
    elif update.message.text == '🔙 Назад':
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
        return ConversationHandler.END
    else:
        await update.message.reply_text('Пожалуйста, отправьте корректный контакт.')
        return GIFT_SUBSCRIPTION_CONTACT


async def handle_gift_subscription_plan(update: Update, context: CallbackContext):
    plan = update.message.text
    if plan == '🔙 Назад':
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
        return ConversationHandler.END
    context.user_data['plan'] = plan
    await update.message.reply_text('Выберите метод оплаты:', reply_markup=payment_method_markup())
    return GIFT_SUBSCRIPTION_PAYMENT_METHOD


async def handle_gift_subscription_payment_method(update: Update, context: CallbackContext):
    payment_method = update.message.text
    if payment_method == '🔙 Назад':
        await update.message.reply_text('Выберите план подписки снова:', reply_markup=subscription_plan_markup())
        return GIFT_SUBSCRIPTION_PLAN
    context.user_data['payment_method'] = payment_method
    if payment_method == '💳 Картой':
        await update.message.reply_text('Введите номер карты:')
    elif payment_method == '₿ Криптовалютой':
        await update.message.reply_text('Введите ваш крипто-адрес:')
    return GIFT_SUBSCRIPTION_PAYMENT_DETAILS


async def handle_gift_subscription_payment_details(update: Update, context: CallbackContext):
    payment_method = context.user_data['payment_method']
    if payment_method == '💳 Картой':
        context.user_data['card_number'] = update.message.text
    elif payment_method == '₿ Криптовалютой':
        context.user_data['crypto_address'] = update.message.text
    await process_gift_payment(update, context)
    await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
    return ConversationHandler.END


async def process_gift_payment(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    recipient_user_id = context.user_data['recipient_user_id']
    recipient_first_name = context.user_data.get('recipient_first_name', '')
    recipient_last_name = context.user_data.get('recipient_last_name', '')
    plan = context.user_data['plan']
    payment_method = context.user_data['payment_method']

    # Map plan names to backend expected values
    plan_mapping = {
        "📅 Месячная подписка": "monthly",
        "📆 Годовая подписка": "yearly"
    }
    plan_value = plan_mapping.get(plan, "")

    payment_data = {
        "user_id": user_id,
        "amount": "10.00" if plan_value == "monthly" else "100.00",  # Example amounts
        "payment_method": payment_method,
    }

    if payment_method == '💳 Картой':
        payment_data["card_number"] = context.user_data['card_number']
    elif payment_method == '₿ Криптовалютой':
        payment_data["crypto_address"] = context.user_data['crypto_address']

    try:
        # Make the payment
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            await update.message.reply_text('✅ Оплата успешно завершена.')
            # Gift the subscription
            gift_data = {
                "user_id": user_id,
                "recipient_id": recipient_user_id,
                "recipient_first_name": recipient_first_name,
                "recipient_last_name": recipient_last_name,
                "plan": plan_value
            }
            gift_response = requests.post(f'{BACKEND_URL}gift-subscription/', json=gift_data)
            if gift_response.status_code == 201:
                await update.message.reply_text(f'🎁 Подписка подарена пользователю!')
            else:
                await update.message.reply_text(
                    f'❌ Ошибка при дарении подписки. Код ответа: {gift_response.status_code}')
        else:
            await update.message.reply_text(f'❌ Ошибка при оплате. Код ответа: {response.status_code}')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка соединения с сервером: {e}')


# Feedback conversation
async def handle_feedback_entry(update: Update, context: CallbackContext):
    await update.message.reply_text('📝 Введите ваш отзыв:')
    return FEEDBACK_MESSAGE


async def handle_feedback_message(update: Update, context: CallbackContext):
    feedback = update.message.text
    user_id = update.message.chat_id

    try:
        response = requests.post(f'{BACKEND_URL}feedback/', json={"user_id": user_id, "message": feedback})
        if response.status_code == 201:
            await update.message.reply_text('✅ Спасибо за ваш отзыв!')
        else:
            await update.message.reply_text(f'❌ Ошибка при отправке отзыва. Код ответа: {response.status_code}')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка соединения с сервером: {e}')
    return ConversationHandler.END


async def handle_profile(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    response = requests.get(f'{BACKEND_URL}user-profile/{user_id}/')
    if response.status_code == 200:
        profile = response.json()
        subscriptions = profile.get('subscriptions', [])
        subscription_info = ''
        for sub in subscriptions:
            plan = sub.get('plan') or ''
            start_date = (sub.get('start_date') or '')[:10]  # Format date as YYYY-MM-DD
            end_date = (sub.get('end_date') or '')[:10]
            # Escape special characters
            plan = escape_markdown(plan.capitalize(), version=2)
            start_date = escape_markdown(start_date, version=2)
            end_date = escape_markdown(end_date, version=2)
            subscription_info += f"\n• План: {plan}, с {start_date} по {end_date}"
        name = profile.get('name') or ''
        name = escape_markdown(name, version=2)
        username = profile.get('username') or ''
        username = escape_markdown(username, version=2)
        subscription_info = escape_markdown(subscription_info if subscription_info else ' Нет активных подписок.',
                                            version=2)
        await update.message.reply_text(
            f"👤 *Профиль*:\nИмя: {name}\nUsername: {username}\n"
            f"Подписки:{subscription_info}",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text('❌ Ошибка при получении данных профиля.')


# Support handler
async def handle_support(update: Update, context: CallbackContext):
    response = requests.get(f'{BACKEND_URL}support/')
    if response.status_code == 200:
        support_info = response.json()
        email = support_info.get('email', 'N/A')
        phone = support_info.get('phone', 'N/A')
        working_hours = support_info.get('working_hours', 'N/A')
        support_text = (
            f"🛠 *Поддержка*:\n"
            f"📧 Email: {email}\n"
            f"📞 Телефон: {phone}\n"
            f"⏰ Время работы: {working_hours}"
        )
        await update.message.reply_text(support_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(f'❌ Ошибка при получении информации поддержки. Код ответа: {response.status_code}')


async def handle_statistics(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    response = requests.get(f'{BACKEND_URL}statistics/{user_id}/')
    if response.status_code == 200:
        stats = response.json()
        total_payments = stats.get('total_payments') or '0.00'
        subscription_count = stats.get('subscription_count') or '0'
        last_payment_date = stats.get('last_payment_date') or 'N/A'
        # Escape data
        total_payments = escape_markdown(str(total_payments), version=2)
        subscription_count = escape_markdown(str(subscription_count), version=2)
        last_payment_date = escape_markdown(str(last_payment_date), version=2)
        await update.message.reply_text(
            f"📊 *Статистика*:\n\nОбщая сумма оплат: {total_payments}\n"
            f"Число подписок: {subscription_count}\n"
            f"Последняя оплата: {last_payment_date}",
            parse_mode='MarkdownV2'
        )
    elif response.status_code == 404:
        await update.message.reply_text('❌ Статистика пока недоступна. Возможно, вы еще не совершали платежей.')
    else:
        await update.message.reply_text(f'❌ Ошибка при получении статистики. Код ответа: {response.status_code}')


# About product handler
async def handle_about_product(update: Update, context: CallbackContext):
    response = requests.get(f'{BACKEND_URL}about/')
    if response.status_code == 200:
        product_info = response.json()
        await update.message.reply_text(
            f"🛍 *Название*: {product_info['name']}\n💵 *Цена за месяц*: {product_info['price_monthly']}\n💳 *Цена за год*: {product_info['price_yearly']}\n\n{product_info['description']}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f'❌ Ошибка при получении информации о продукте. Код ответа: {response.status_code}')


# Handlers for the conversation flows
buy_subscription_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^💼 Приобрести себе$'), handle_buy_subscription_entry)],
    states={
        BUY_SUBSCRIPTION_EMAIL: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_email)],
        BUY_SUBSCRIPTION_PLAN: [MessageHandler(filters.Regex('^(📅 Месячная подписка|📆 Годовая подписка|🔙 Назад)$'),
                                               handle_buy_subscription_plan)],
        BUY_SUBSCRIPTION_PAYMENT_METHOD: [MessageHandler(filters.Regex('^(💳 Картой|₿ Криптовалютой|🔙 Назад)$'),
                                                         handle_buy_subscription_payment_method)],
        BUY_SUBSCRIPTION_PAYMENT_DETAILS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_payment_details)],
    },
    fallbacks=[MessageHandler(filters.Regex('^🔙 Назад$'), main_menu_handler)],
)

gift_subscription_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^🎁 Подарить подписку$'), handle_gift_subscription_entry)],
    states={
        GIFT_SUBSCRIPTION_CONTACT: [MessageHandler((filters.CONTACT | filters.Regex('^🔙 Назад$')) & (~filters.COMMAND),
                                                   handle_gift_subscription_contact)],
        GIFT_SUBSCRIPTION_PLAN: [MessageHandler(filters.Regex('^(📅 Месячная подписка|📆 Годовая подписка|🔙 Назад)$'),
                                                handle_gift_subscription_plan)],
        GIFT_SUBSCRIPTION_PAYMENT_METHOD: [MessageHandler(filters.Regex('^(💳 Картой|₿ Криптовалютой|🔙 Назад)$'),
                                                          handle_gift_subscription_payment_method)],
        GIFT_SUBSCRIPTION_PAYMENT_DETAILS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_gift_subscription_payment_details)],
    },
    fallbacks=[MessageHandler(filters.Regex('^🔙 Назад$'), main_menu_handler)],
)

feedback_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^📩 Оставить отзыв$'), handle_feedback_entry)],
    states={
        FEEDBACK_MESSAGE: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_feedback_message)],
    },
    fallbacks=[MessageHandler(filters.Regex('^🔙 Назад$'), main_menu_handler)],
)

# Add handlers to the application
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.Regex('^🚀 Начать$'), send_documents))
application.add_handler(MessageHandler(filters.Regex('^✅ Согласен$'), consent_callback))
application.add_handler(
    MessageHandler(filters.Regex('^(ℹ️ О продукте|🛠 Поддержка|📊 Моя Статистика|👤 Мой Профиль)$'), main_menu_handler))

# Add conversation handlers
application.add_handler(buy_subscription_conv_handler)
application.add_handler(gift_subscription_conv_handler)
application.add_handler(feedback_conv_handler)

if __name__ == '__main__':
    application.run_polling()
