# bot/buttons.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def language_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='en')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='ru')],
    ]
    return InlineKeyboardMarkup(keyboard)
