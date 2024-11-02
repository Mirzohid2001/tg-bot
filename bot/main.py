# bot/main.py

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.registration import start, language_selection, send_documents, consent_callback
from bot.handlers.main_menu import main_menu_handler, show_main_menu
from bot.handlers.buy_subscription import (
    handle_buy_subscription_entry,
    handle_buy_subscription_email,
    handle_buy_subscription_plan,
    handle_buy_subscription_payment_method,
    handle_buy_subscription_payment_details, handle_enter_new_card, handle_use_saved_card,
    handle_buy_subscription_card_expiry,
)
from bot.handlers.gift_subscription import (
    handle_gift_subscription_entry,
    handle_gift_subscription_contact,
    handle_gift_subscription_plan,
    handle_gift_subscription_payment_method,
    handle_gift_subscription_payment_details,
)
from bot.handlers.methods_manuals import (
    handle_methods_manuals_entry,
    methods_menu_handler,
    method_details_handler,
)
from bot.handlers.feedback import handle_feedback_entry, handle_feedback_message
from bot.handlers.support import handle_support, support_menu_handler
from bot.handlers.profile import handle_profile
from bot.handlers.statistics import handle_statistics
from bot.handlers.about_product import handle_about_product
from bot.handlers.save_card import handle_save_card, save_card_number, save_card_expiry
from bot.utilities import get_text
from bot.constants import (
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
    SAVE_CARD_NUMBER,
    SAVE_CARD_EXPIRY, BUY_SUBSCRIPTION_CARD_EXPIRY,
)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize the application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Help command
async def help_command(update, context):
    help_text = get_text(context, 'help_text')
    await update.message.reply_text(help_text, parse_mode='Markdown')

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
            CallbackQueryHandler(
                handle_buy_subscription_plan,
                pattern='^(monthly_subscription|yearly_subscription|back_to_email|back_to_main)$',
            )
        ],
        BUY_SUBSCRIPTION_PAYMENT_METHOD: [
            CallbackQueryHandler(
                handle_buy_subscription_payment_method,
                pattern='^(pay_card|pay_crypto|back_to_plan)$',
            )
        ],
        BUY_SUBSCRIPTION_PAYMENT_DETAILS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_payment_details),
            CallbackQueryHandler(handle_use_saved_card, pattern='^use_saved_card$'),
            CallbackQueryHandler(handle_enter_new_card, pattern='^enter_new_card$'),
            CallbackQueryHandler(handle_buy_subscription_payment_method, pattern='^back_to_payment_method$'),
        ],
        BUY_SUBSCRIPTION_CARD_EXPIRY: [  # Добавлено новое состояние
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buy_subscription_card_expiry),
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
application.add_handler(save_card_conv_handler)


if __name__ == '__main__':
    application.run_polling()
