import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TELEGRAM_BOT_TOKEN = '7901466690:AAFtUArAc1ELvSbdDL53SlgnZ1mUIPvHRgQ'
BACKEND_URL = 'http://127.0.0.1:8000/subscription/'  # Backend URL

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


def register_user(user_id, username):
    response = requests.post(f'{BACKEND_URL}register/', json={"user_id": user_id, "username": username})
    if response.status_code == 201:
        return "Вы успешно зарегистрированы\\! 🎉"
    elif response.status_code == 200:
        return "Вы уже зарегистрированы\\! ✔️"
    else:
        return "Ошибка регистрации\\. ❌"



async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    username = update.message.chat.username
    registration_status = register_user(user_id, username)

    # Foydalanuvchiga boshlash tugmasi yuborish
    keyboard = [[KeyboardButton("🚀 Начать")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f'{registration_status}', reply_markup=reply_markup)


async def send_documents(update: Update, context: CallbackContext):
    agreement_text = """
    *Пользовательское соглашение*:
    1\\. Ваши данные будут использоваться в соответствии с нашей политикой конфиденциальности\\.
    2\\. Вы обязуетесь использовать наш сервис в соответствии с законодательством и не нарушать права других пользователей\\.

    *Политика конфиденциальности*:
    1\\. Мы собираем и обрабатываем ваши личные данные в целях предоставления качественного сервиса\\.
    2\\. Ваши данные не будут переданы третьим лицам без вашего согласия\\.
    """

    await update.message.reply_text(agreement_text, parse_mode='MarkdownV2')
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
        await handle_buy_subscription(update, context)
    elif message == '🎁 Подарить подписку':
        await handle_gift_subscription(update, context)
    elif message == 'ℹ️ О продукте':
        await handle_about_product(update, context)
    elif message == '🛠 Поддержка':
        await handle_support(update, context)
    elif message == '📊 Моя Статистика':
        await handle_statistics(update, context)
    elif message == '👤 Мой Профиль':
        await handle_profile(update, context)
    elif message == '📩 Оставить отзыв':
        await handle_feedback(update, context)



async def handle_buy_subscription(update: Update, context: CallbackContext):
    await update.message.reply_text('✉️ Введите ваш email для получения чека:')
    context.user_data['next_step'] = 'email'


async def handle_email(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'email':
        email = update.message.text
        context.user_data['email'] = email
        context.user_data['next_step'] = 'choose_plan'
        await update.message.reply_text(f'Ваш email {email} сохранен. Выберите план подписки:',
                                        reply_markup=subscription_plan_markup())


def subscription_plan_markup():
    keyboard = [
        [KeyboardButton("📅 Месячная подписка")],
        [KeyboardButton("📆 Годовая подписка")],
        [KeyboardButton("🔙 Назад")]  # Orqaga qaytish tugmasi
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# To'lov usuli uchun klaviatura
def payment_method_markup():
    keyboard = [
        [KeyboardButton("💳 Картой")],
        [KeyboardButton("₿ Криптовалютой")],
        [KeyboardButton("🔙 Назад")]  # Orqaga qaytish tugmasi
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# Obuna tanlash va to'lov usulini tanlash
async def handle_plan_selection(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'choose_plan':
        plan = update.message.text
        context.user_data['plan'] = plan
        context.user_data['next_step'] = 'choose_payment_method'
        await update.message.reply_text(
            'Выберите метод оплаты:',
            reply_markup=payment_method_markup()
        )


# To'lov usulini tanlash va "Назад" tugmasini boshqarish
async def handle_payment_method(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'choose_payment_method':
        payment_method = update.message.text

        # Agar foydalanuvchi "Назад" ni tanlasa
        if payment_method == '🔙 Назад':
            context.user_data['next_step'] = 'choose_plan'
            await update.message.reply_text(
                'Выберите план подписки снова:',
                reply_markup=subscription_plan_markup()
            )
        else:
            context.user_data['payment_method'] = payment_method
            if payment_method == '💳 Картой':
                context.user_data['next_step'] = 'enter_card_number'
                await update.message.reply_text('Введите номер карты:')
            elif payment_method == '₿ Криптовалютой':
                context.user_data['next_step'] = 'enter_crypto_address'
                await update.message.reply_text('Введите ваш крипто-адрес:')


# Kartani yoki kripto manzilni kiritish va "Назад" tugmasi
async def handle_payment_details(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'enter_card_number':
        card_number = update.message.text
        context.user_data['card_number'] = card_number
        await process_payment(update, context)
    elif context.user_data.get('next_step') == 'enter_crypto_address':
        crypto_address = update.message.text
        context.user_data['crypto_address'] = crypto_address
        await process_payment(update, context)
    elif update.message.text == '🔙 Назад':
        context.user_data['next_step'] = 'choose_payment_method'
        await update.message.reply_text(
            'Выберите метод оплаты:',
            reply_markup=payment_method_markup()
        )


# To'lovni amalga oshirish
async def process_payment(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    plan = context.user_data['plan']
    email = context.user_data['email']
    payment_method = context.user_data['payment_method']

    payment_data = {
        "user_id": user_id,
        "plan": plan,
        "email": email,
        "payment_method": payment_method,
    }

    if payment_method == '💳 Картой':
        payment_data["card_number"] = context.user_data['card_number']
    elif payment_method == '₿ Криптовалютой':
        payment_data["crypto_address"] = context.user_data['crypto_address']

    try:
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            await update.message.reply_text('✅ Оплата успешно завершена.')
            await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu_markup())
        else:
            await update.message.reply_text(f'❌ Ошибка при оплате. Код ответа: {response.status_code}')
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f'❌ Ошибка соединения с сервером: {e}')


# Profil ma'lumotlarini olish
async def handle_profile(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    response = requests.get(f'{BACKEND_URL}user-profile/{user_id}/')
    if response.status_code == 200:
        profile = response.json()
        await update.message.reply_text(
            f"👤 *Профиль*:\nИмя: {profile['name']}\nUsername: {profile['username']}\n"
            f"Подписки: {profile['subscriptions']}\nПлатежи: {profile['payments']}",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text('❌ Ошибка при получении данных профиля.')


async def handle_feedback(update: Update, context: CallbackContext):
    await update.message.reply_text('📝 Введите ваш отзыв:')
    context.user_data['next_step'] = 'feedback'


async def handle_feedback_message(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'feedback':
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


async def handle_support(update: Update, context: CallbackContext):
    response = requests.get(f'{BACKEND_URL}help/')
    if response.status_code == 200:
        help_sections = response.json()
        help_text = "\n\n".join([f"🛠 *{section['title']}*: {section['content']}" for section in help_sections])
        await update.message.reply_text(help_text, parse_mode='MarkdownV2')
    else:
        await update.message.reply_text(f'❌ Ошибка при получении справки. Код ответа: {response.status_code}')



async def handle_statistics(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    response = requests.get(f'{BACKEND_URL}statistics/{user_id}/')
    if response.status_code == 200:
        stats = response.json()
        await update.message.reply_text(
            f"📊 *Статистика*:\n\nОбщая сумма оплат: {stats['total_payments']}\nЧисло подписок: {stats['subscription_count']}\nПоследняя оплата: {stats['last_payment_date']}",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text('❌ Ошибка при получении статистики.')


async def handle_about_product(update: Update, context: CallbackContext):
    response = requests.get(f'{BACKEND_URL}about/')
    if response.status_code == 200:
        product_info = response.json()
        await update.message.reply_text(
            f"🛍 *Название*: {product_info['name']}\n💵 *Цена за месяц*: {product_info['price_monthly']}\n💳 *Цена за год*: {product_info['price_yearly']}",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text(
            f'❌ Ошибка при получении информации о продукте. Код ответа: {response.status_code}')


async def handle_gift_subscription(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ID получателя подарка и выберите план подписки:")
    context.user_data['next_step'] = 'gift_subscription'


async def handle_gift_subscription_process(update: Update, context: CallbackContext):
    if context.user_data.get('next_step') == 'gift_subscription':
        gift_data = update.message.text.split(' ')
        if len(gift_data) == 2:
            recipient_id, plan = gift_data
            user_id = update.message.chat_id

            response = requests.post(f'{BACKEND_URL}gift-subscription/', json={
                "user_id": user_id,
                "recipient_id": recipient_id,
                "plan": plan
            })

            if response.status_code == 201:
                await update.message.reply_text(f'🎁 Подписка подарена пользователю с ID: {recipient_id}')
            else:
                await update.message.reply_text(f'❌ Ошибка при дарении подписки. Код ответа: {response.status_code}')
        else:
            await update.message.reply_text('❌ Некорректные данные. Введите ID и план подписки через пробел.')


# Xandllerlar
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(🚀 Начать)$'), send_documents))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(✅ Согласен)$'), consent_callback))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex(
    '^(💼 Приобрести себе|🎁 Подарить подписку|ℹ️ О продукте|🛠 Поддержка|📊 Моя Статистика|👤 Мой Профиль|📩 Оставить отзыв)$'),
                                       main_menu_handler))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_email))
application.add_handler(
    MessageHandler(filters.TEXT & filters.Regex('^(📅 Месячная подписка|📆 Годовая подписка)$'), handle_plan_selection))
application.add_handler(
    MessageHandler(filters.TEXT & filters.Regex('^(💳 Картой|₿ Криптовалютой|🔙 Назад)$'), handle_payment_method))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_payment_details))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_feedback_message))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_gift_subscription_process))

if __name__ == '__main__':
    application.run_polling()
