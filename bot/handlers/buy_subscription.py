# bot/handlers/buy_subscription.py
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from bot.utilities import (
    subscription_plan_markup,
    payment_method_markup,
    back_button_markup,
    get_text,

    save_card_data,
)
from bot.handlers.main_menu import show_main_menu
from bot.constants import (
    BUY_SUBSCRIPTION_EMAIL,
    BUY_SUBSCRIPTION_PLAN,
    BUY_SUBSCRIPTION_PAYMENT_METHOD,
    BUY_SUBSCRIPTION_PAYMENT_DETAILS, BUY_SUBSCRIPTION_CARD_EXPIRY,
)
from bot.config import BACKEND_URL


async def handle_buy_subscription_entry(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "✉️ Please enter your email to receive the receipt:"
    else:
        text = "✉️ Пожалуйста, введите ваш email для получения чека:"
    await update.callback_query.message.edit_text(
        text, reply_markup=back_button_markup('back_to_main', context)
    )
    return BUY_SUBSCRIPTION_EMAIL


async def handle_buy_subscription_email(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = (
            f"Your email {email} has been saved.\n\n"
            "**Step 1/3: Choose a subscription plan:**"
        )
    else:
        text = (
            f"Ваш email {email} сохранен.\n\n"
            "**Шаг 1/3: Выберите план подписки:**"
        )
    await update.message.reply_text(
        text, reply_markup=subscription_plan_markup(context), parse_mode='Markdown'
    )
    return BUY_SUBSCRIPTION_PLAN


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
        await query.message.edit_text(
            text, reply_markup=back_button_markup('back_to_main', context)
        )
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
    await query.message.edit_text(
        text, reply_markup=payment_method_markup(context), parse_mode='Markdown'
    )
    return BUY_SUBSCRIPTION_PAYMENT_METHOD


async def handle_buy_subscription_payment_method(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    payment_method = query.data
    language = context.user_data.get('language', 'en')
    user_id = update.effective_chat.id

    if payment_method == 'back_to_plan':
        # Go back to plan selection
        if language == 'en':
            text = "**Step 1/3: Choose a subscription plan:**"
        else:
            text = "**Шаг 1/3: Выберите план подписки:**"
        await query.message.edit_text(
            text, reply_markup=subscription_plan_markup(context), parse_mode='Markdown'
        )
        return BUY_SUBSCRIPTION_PLAN
    elif payment_method == 'pay_card':
        context.user_data['payment_method'] = 'card'
        # Check if user has a saved card
        saved_card = get_saved_card(user_id)
        if saved_card:
            # Offer to use the saved card or enter a new one
            if language == 'en':
                text = "💳 You have a saved card. Do you want to use it?"
                keyboard = [
                    [InlineKeyboardButton("💳 Use Saved Card", callback_data='use_saved_card')],
                    [InlineKeyboardButton("💳 Enter New Card", callback_data='enter_new_card')],
                    [InlineKeyboardButton("🔙 Back", callback_data='back_to_payment_method')],
                ]
            else:
                text = "💳 У вас есть сохраненная карта. Хотите использовать ее?"
                keyboard = [
                    [InlineKeyboardButton("💳 Использовать сохраненную карту", callback_data='use_saved_card')],
                    [InlineKeyboardButton("💳 Ввести новую карту", callback_data='enter_new_card')],
                    [InlineKeyboardButton("🔙 Назад", callback_data='back_to_payment_method')],
                ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup)
            return BUY_SUBSCRIPTION_PAYMENT_DETAILS
        else:
            # No saved card, ask to enter card details
            if language == 'en':
                text = "💳 Please enter your card number:"
            else:
                text = "💳 Пожалуйста, введите номер вашей карты:"
            await query.message.edit_text(
                text, reply_markup=back_button_markup('back_to_payment_method', context)
            )
            return BUY_SUBSCRIPTION_PAYMENT_DETAILS
    elif payment_method == 'pay_crypto':
        context.user_data['payment_method'] = 'crypto'
        # Ask for cryptocurrency wallet address
        if language == 'en':
            text = "💰 Please enter your cryptocurrency wallet address:"
        else:
            text = "💰 Пожалуйста, введите адрес вашего криптокошелька:"
        await query.message.edit_text(
            text, reply_markup=back_button_markup('back_to_payment_method', context)
        )
        return BUY_SUBSCRIPTION_PAYMENT_DETAILS


async def handle_buy_subscription_payment_details(update: Update, context: CallbackContext):
    payment_method = context.user_data.get('payment_method')
    if payment_method == 'card':
        if context.user_data.get('use_saved_card'):
            # Use saved card
            await process_payment(update, context, use_saved_card=True)
            await show_main_menu(update, context)
            return ConversationHandler.END
        else:
            card_number = update.message.text
            context.user_data['card_number'] = card_number
            # Ask for card expiry date
            language = context.user_data.get('language', 'en')
            if language == 'en':
                text = "💳 Please enter your card expiry date (MM/YY):"
            else:
                text = "💳 Пожалуйста, введите срок действия карты (ММ/ГГ):"
            await update.message.reply_text(text)
            return BUY_SUBSCRIPTION_PAYMENT_DETAILS + 1  # Move to next state
    elif payment_method == 'crypto':
        wallet_address = update.message.text
        context.user_data['wallet_address'] = wallet_address
        # Process cryptocurrency payment
        await process_crypto_payment(update, context)
        await show_main_menu(update, context)
        return ConversationHandler.END



async def handle_buy_subscription_card_expiry(update: Update, context: CallbackContext):
    expiry_date = update.message.text.strip()
    # Regular expression to match accepted date formats
    if not re.match(r'^(0[1-9]|1[0-2])/(?:\d{2}|\d{4})$|^(0[1-9]|1[0-2])-(?:\d{4})$', expiry_date):
        await update.message.reply_text("❌ Invalid date format. Please enter the expiry date in one of the accepted formats: MM/YY, MM-YYYY, or MM/YYYY.")
        return BUY_SUBSCRIPTION_CARD_EXPIRY
    context.user_data['expiry_date'] = expiry_date
    # Proceed to process payment
    await process_payment(update, context, save_card=True)
    await show_main_menu(update, context)
    return ConversationHandler.END


async def process_payment(update: Update, context: CallbackContext, use_saved_card=False, save_card=False):
    user_id = update.effective_chat.id
    plan = context.user_data['plan']
    email = context.user_data['email']
    payment_method = 'card'
    language = context.user_data.get('language', 'en')

    # Map plan names to backend values
    plan_mapping = {
        "monthly_subscription": "monthly",
        "yearly_subscription": "yearly",
    }
    plan_value = plan_mapping.get(plan, "")

    # Get subscription price
    price_response = requests.get(f'{BACKEND_URL}plan-price/{plan_value}/')
    if price_response.status_code == 200:
        price_info = price_response.json()
        amount = price_info.get('price', '0.00')
    else:
        amount = '0.00'

    if use_saved_card:
        # Get saved card details
        saved_card = get_saved_card(user_id)
        card_number = saved_card.get('card_number')
        expiry_date = saved_card.get('expiry_date')
    else:
        card_number = context.user_data.get('card_number')
        expiry_date = context.user_data.get('expiry_date')

    payment_data = {
        "user_id": user_id,
        "plan": plan_value,
        "email": email,
        "amount": amount,
        "payment_method": payment_method,
        "card_number": card_number,
        "expiry_date": expiry_date,
        "transaction_id": None,  # Assuming no transaction ID in this example
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
            subscription_response = requests.post(
                f'{BACKEND_URL}subscription/',
                json={"user_id": user_id, "plan": plan_value, "email": email},
            )
            if save_card:
                # Ensure all required data is available
                if card_number and expiry_date:
                    save_card_data(user_id, card_number, expiry_date)
                else:
                    await update.message.reply_text("❌ Error saving card.")
            if subscription_response.status_code == 201:
                await update.message.reply_text(text_subscription)
                # Save card if needed
                if save_card:
                    save_card_data(user_id, card_number, expiry_date)
            else:
                await update.message.reply_text(
                    f"❌ Error activating subscription. Response code: {subscription_response.status_code}"
                )
        else:
            await update.message.reply_text(
                f"❌ Error during payment. Response code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error connecting to the server: {e}")


async def process_crypto_payment(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    plan = context.user_data['plan']
    email = context.user_data['email']
    wallet_address = context.user_data.get('wallet_address')
    payment_method = 'crypto'
    language = context.user_data.get('language', 'en')

    # Map plan names to backend values
    plan_mapping = {
        "monthly_subscription": "monthly",
        "yearly_subscription": "yearly",
    }
    plan_value = plan_mapping.get(plan, "")

    # Get subscription price in crypto
    price_response = requests.get(f'{BACKEND_URL}plan-price/{plan_value}/?currency=crypto')
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
        "wallet_address": wallet_address,
        "transaction_id": None,  # Assuming no transaction ID in this example
    }

    # Process crypto payment (Assuming payment is always successful in this example)
    try:
        response = requests.post(f'{BACKEND_URL}payment/', json=payment_data)
        if response.status_code == 201:
            if language == 'en':
                text_success = "✅ Cryptocurrency payment was successful."
                text_subscription = "✅ Subscription has been activated."
            else:
                text_success = "✅ Оплата криптовалютой прошла успешно."
                text_subscription = "✅ Подписка активирована."
            await update.message.reply_text(text_success)
            # Activate subscription
            subscription_response = requests.post(
                f'{BACKEND_URL}subscription/',
                json={"user_id": user_id, "plan": plan_value, "email": email},
            )
            if subscription_response.status_code == 201:
                await update.message.reply_text(text_subscription)
            else:
                await update.message.reply_text(
                    f"❌ Error activating subscription. Response code: {subscription_response.status_code}"
                )
        else:
            await update.message.reply_text(
                f"❌ Error during payment. Response code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error connecting to the server: {e}")


def get_saved_card(user_id):
    # Function to get the user's saved card from the backend
    try:
        response = requests.get(f'{BACKEND_URL}user-card/{user_id}/')
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching saved card: {e}")
        return None


# Handler for using saved card
async def handle_use_saved_card(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data['use_saved_card'] = True
    # Process payment using saved card
    await process_payment(update, context, use_saved_card=True)
    await show_main_menu(update, context)
    return ConversationHandler.END


# Handler for entering new card details
async def handle_enter_new_card(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    language = context.user_data.get('language', 'en')
    if language == 'en':
        text = "💳 Please enter your card number:"
    else:
        text = "💳 Пожалуйста, введите номер вашей карты:"
    await query.message.edit_text(
        text, reply_markup=back_button_markup('back_to_payment_method', context)
    )
    return BUY_SUBSCRIPTION_PAYMENT_DETAILS
