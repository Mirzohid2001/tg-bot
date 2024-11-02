# bot/language.py

LANGUAGES = {
    'en': {
        'welcome': "Welcome!",
        'choose_language': "Please select your language:",
        'start_over': "To start over, send the /start command.",
        'profile_subscription_info': (
            "📝 *Subscription Information*:\n"
            "• Plan: {plan}\n"
            "• Expires At: {expires_at}\n"
        ),
        'profile_card_info': (
            "💳 *Card Information*:\n"
            "• Card Number: {card_number}\n"
            "• Expiry Date: {expiry_date}\n"
        ),
        'profile_subscription_info': (
            "📝 *Subscription Information*:\n"
            "• Plan: {plan}\n"
            "• Expires At: {expires_at}\n"
        ),

        'welcome_back': "Welcome back, {username}! 🎉",
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
        'profile_card_info': (
            "💳 *Saved Card Information*:\n"
            "• Card Number: {card_number}\n"
            "• Expiry Date: {expiry_date}\n"
        ),
    },
    'ru': {
        'welcome': "Добро пожаловать!",
        'choose_language': "Пожалуйста, выберите ваш язык:",
        'start_over': "Чтобы начать сначала, отправьте команду /start.",
        'welcome_back': "С возвращением, {username}! 🎉",
        'profile_subscription_info': (
            "📝 *Информация о подписке*:\n"
            "• План: {plan}\n"
            "• Действует до: {expires_at}\n"
        ),

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

        'profile_card_info': (
            "💳 *Информация о карте*:\n"
            "• Номер карты: {card_number}\n"
            "• Срок действия: {expiry_date}\n"
        ),
        'profile_subscription_info': (
            "📝 *Информация о подписке*:\n"
            "• План: {plan}\n"
            "• Действует до: {expires_at}\n"
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
        'profile_card_info': (
            "💳 *Информация о сохраненной карте*:\n"
            "• Номер карты: {card_number}\n"
            "• Срок действия: {expiry_date}\n"
        ),
    }
}
