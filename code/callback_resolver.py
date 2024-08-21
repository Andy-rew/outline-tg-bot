from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommandScopeChat

from code.config_commands import user_commands
from code.exceptions import AbobaError
from code.keys_service import get_key_info
from code.outline import get_outline_client
from code.user_service import approve_new_user
from code.utils import CallbackEnum, _join_text, _wrap_as_markdown

client = get_outline_client()


async def resolve_callback(bot: AsyncTeleBot, call: types.CallbackQuery):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    action = call.data.split(' ')[0]
    query_worker_id = call.data.split(' ')[1]

    if query_worker_id != str(call.from_user.id):
        await bot.answer_callback_query(call.id, "Permission denied")
        return

    if action not in CallbackEnum.__members__:
        await bot.answer_callback_query(call.id, "Action not found")

    if action == CallbackEnum.delete_key.value:
        data_id = call.data.split(' ')[2]

        delete_status_ok = client.delete_key(data_id)

        if delete_status_ok:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Success deletion\nID: {data_id}')
            await bot.answer_callback_query(call.id, "Done")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Failed deletion")
            await bot.answer_callback_query(call.id, "Failed")

    elif action == CallbackEnum.approve_user.value:
        data_id = call.data.split(' ')[2]

        approved_user = approve_new_user(data_id)
        approve_status_ok = approved_user.is_approved

        if approve_status_ok:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Success approve\nID: {data_id}')
            await bot.answer_callback_query(call.id, "Done")

            sent_message = await bot.send_message(approved_user.tg_id,
                                                  "You are approved by admin and can create " +
                                                  f"{approved_user.keys_count} VPN keys")

            await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=sent_message.chat.id))

        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Failed approve")
            await bot.answer_callback_query(call.id, "Failed")

    elif action == CallbackEnum.view_key.value:

        data_id = call.data.split(' ')[2]
        try:
            key = get_key_info(query_worker_id, data_id)
        except AbobaError as err:
            await bot.answer_callback_query(call.id, f"{err}")
            return

        text = _join_text('Got key', f'ID: {key.key_id}', f'Name: {key.name}', 'Key in next message:')
        await bot.send_message(query_worker_id, text)
        await bot.send_message(query_worker_id, _wrap_as_markdown(key.access_url), parse_mode='Markdown')
        if message.chat.type != "private":
            await bot.answer_callback_query(call.id, "Credentials sent to your DM.")

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Success')

    elif action == CallbackEnum.cancel.value:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Canceled')
        await bot.answer_callback_query(call.id, "Canceled")
