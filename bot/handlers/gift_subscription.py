# bot/handlers/gift_subscription.py

import requests
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from bot.utilities import (
    subscription_plan_markup,
    payment_method_markup,
    back_button_markup,
    get_text,
)
from bot.handlers.main_menu import show_main_menu
from bot.constants import (
    GIFT_SUBSCRIPTION_CONTACT,
    GIFT_SUBSCRIPTION_PLAN,
    GIFT_SUBSCRIPTION_PAYMENT_METHOD,
    GIFT_SUBSCRIPTION_PAYMENT_DETAILS,
)
from bot.config import BACKEND_URL

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
