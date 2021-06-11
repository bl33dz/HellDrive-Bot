from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram import ParseMode, ChatAction
from functools import wraps
from drive import bypassLimit

def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

send_typing_action = send_action(ChatAction.TYPING)

@send_typing_action
def start(update, context):
	update.message.reply_text("""Welcome to HellDrive Bot v1

This bot can bypass google drive download limit.

Usage: 
- /bypass <fileID/URL>
- /supportedURL""")

@send_typing_action
def bypass(update, context):
	url = context.args[0]
	resp = bypassLimit(url)
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=resp)

@send_typing_action
def supportedURL(update, context):
	update.message.reply_text("""Supported URL:
- https://drive.google.com/file/d/[FILEID]/
- https://drive.google.com/uc?id=[FILEID]
 - [FILEID]""")

@send_typing_action
def unknown(update, context):
	resp = "Sorry, I didn't understand what you mean."
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=resp)


updater = Updater('[YOUR_BOT_TOKEN]', use_context=True)
unknown_handler = MessageHandler(Filters.command | Filters.text, unknown)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('bypass', bypass))
updater.dispatcher.add_handler(CommandHandler('supportedURL', supportedURL))
updater.dispatcher.add_handler(unknown_handler)

try:
	updater.start_polling()
except KeyboardInterrupt:
    updater.stop_polling()
    sys.exit(0)
