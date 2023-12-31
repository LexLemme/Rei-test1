"""
MIT License

Copyright (c) 2022 Arsh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import html
from typing import List

from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from Mei import dispatcher
from Mei.modules.helper_funcs.chat_status import bot_admin, can_pin, user_admin
from Mei.modules.log_channel import loggable
from Mei.modules.sql import pin_sql as sql

PMW_GROUP = 12


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]

    is_group = chat.type not in ["private", "channel"]

    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        is_silent = (
            args[0].lower() not in ["notify", "loud", "violent"] if args else True
        )
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise
        sql.add_mid(chat.id, prev_message.message_id)
        user = update.effective_user  # type: Optional[User]
        return f"<b>{html.escape(chat.title)}:</b>\n#PINNED\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"

    return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(bot: Bot, update: Update) -> str:
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message != "Chat_not_modified":
            raise
    sql.remove_mid(chat.id)
    return f"<b>{html.escape(chat.title)}:</b>\n#UNPINNED\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def anti_channel_pin(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    if not args:
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.add_acp_o(str(chat.id), True)
        update.effective_message.reply_text(
            "I'll try to unpin Telegram Channel messages!"
        )
        return f"<b>{html.escape(chat.title)}:</b>\n#ANTI_CHANNEL_PIN\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nHas toggled ANTI CHANNEL PIN to <code>ON</code>."
    elif args[0].lower() in ("off", "no"):
        sql.add_acp_o(str(chat.id), False)
        update.effective_message.reply_text("I won't unpin Telegram Channel Messages!")
        return f"<b>{html.escape(chat.title)}:</b>\n#ANTI_CHANNEL_PIN\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nHas toggled ANTI CHANNEL PIN to <code>OFF</code>."
    else:
        # idek what you're writing, say yes or no
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")
        return ""


@run_async
@bot_admin
@user_admin
@loggable
def clean_linked_channel(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    if not args:
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.add_ldp_m(str(chat.id), True)
        update.effective_message.reply_text(
            "I'll try to delete Telegram Channel messages!"
        )
        return f"<b>{html.escape(chat.title)}:</b>\n#CLEAN_CHANNEL_MESSAGES\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nHas toggled DELETE CHANNEL MESSAGES to <code>ON</code>."
    elif args[0].lower() in ("off", "no"):
        sql.add_ldp_m(str(chat.id), False)
        update.effective_message.reply_text("I won't delete Telegram Channel Messages!")
        return f"<b>{html.escape(chat.title)}:</b>\n#CLEAN_CHANNEL_MESSAGES\n<b>Admin:</b> {mention_html(user.id, user.first_name)}\nHas toggled DELETE CHANNEL MESSAGES to <code>OFF</code>."
    else:
        # idek what you're writing, say yes or no
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")
        return ""


@run_async
def amwltro_conreko(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    sctg = sql.get_current_settings(chat.id)
    """we apparently do not receive any update for PINned messages
    """
    if sctg and sctg.message_id != 0 and message.from_user.id == 777000:
        if sctg.suacpmo:
            try:
                bot.unpin_chat_message(chat.id)
            except BaseException:
                pass
            pin_chat_message(bot, chat.id, sctg.message_id, True)
        if sctg.scldpmo:
            try:
                message.delete()
            except BaseException:
                pass
            pin_chat_message(bot, chat.id, sctg.message_id, True)


def pin_chat_message(bot, chat_id, message_id, is_silent):
    try:
        bot.pinChatMessage(chat_id, message_id, disable_notification=is_silent)
    except BadRequest:
        """else:
        raise"""


__help__ = """

*Admin only:*
 - /pin: silently pins the message replied to
       : add 'loud' or 'notify' to give notifs to users.
 - /unpin: unpins the currently pinned message
 - /antichannelpin <yes/no/on/off>: Don't let telegram auto-pin linked channels.
 - /cleanlinked <yes/no/on/off>: Delete messages sent by the linked channel.

Note:

When using antichannel pins, make sure to use the /unpin command,
instead of doing it manually.

Otherwise, the old message will get re-pinned when the channel sends any messages.
"""

__mod_name__ = "Pins"


PIN_HANDLER = CommandHandler("pin", pin, pass_args=True, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)
ATCPIN_HANDLER = CommandHandler(
    "antichannelpin", anti_channel_pin, pass_args=True, filters=Filters.group
)
CLCLDC_HANDLER = CommandHandler(
    "cleanlinked", clean_linked_channel, pass_args=True, filters=Filters.group
)
AMWLTRO_HANDLER = MessageHandler(
    Filters.forwarded & Filters.group, amwltro_conreko, edited_updates=False
)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(ATCPIN_HANDLER)
dispatcher.add_handler(CLCLDC_HANDLER)
dispatcher.add_handler(AMWLTRO_HANDLER, PMW_GROUP)
