# bot/handlers/main_menu.py

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from bot.utilities import main_menu_markup, get_text

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
        from bot.handlers.buy_subscription import handle_buy_subscription_entry
        return await handle_buy_subscription_entry(update, context)
    elif message == 'gift_subscription':
        from bot.handlers.gift_subscription import handle_gift_subscription_entry
        return await handle_gift_subscription_entry(update, context)
    elif message == 'methods_manuals':
        from bot.handlers.methods_manuals import handle_methods_manuals_entry
        return await handle_methods_manuals_entry(update, context)
    elif message == 'about_product':
        from bot.handlers.about_product import handle_about_product
        await handle_about_product(update, context)
    elif message == 'statistics':
        from bot.handlers.statistics import handle_statistics
        await handle_statistics(update, context)
    elif message == 'profile':
        from bot.handlers.profile import handle_profile
        await handle_profile(update, context)
    elif message == 'feedback':
        from bot.handlers.feedback import handle_feedback_entry
        return await handle_feedback_entry(update, context)
    elif message == 'support':
        from bot.handlers.support import handle_support
        return await handle_support(update, context)
    elif message == 'save_card':
        from bot.handlers.save_card import handle_save_card
        return await handle_save_card(update, context)
    elif message == 'back_to_main':
        await show_main_menu(update, context)
        return ConversationHandler.END
