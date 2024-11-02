# bot/handlers/help.py

from telegram import Update
from telegram.ext import CallbackContext



async def help_command(update: Update, context: CallbackContext):
    from bot.utilities import get_text
    help_text = get_text(context, 'help_text')
    await update.message.reply_text(help_text, parse_mode='Markdown')
