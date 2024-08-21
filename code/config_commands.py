from telebot.types import BotCommand

admin_commands = [
    BotCommand(command='start', description='Start'),
    BotCommand(command='admin_metrics', description='All keys statistic'),
    BotCommand(command='metrics', description='My keys statistic'),
    BotCommand(command='new_key', description='Add new key'),
    BotCommand(command='get_key', description='Get credentials for existing key'),
    BotCommand(command='users_for_approve', description='Get users for approve'),
    BotCommand(command='admin_delete_key', description='Delete old key'),
    BotCommand(command='delete_key', description='Delete old key'),
    BotCommand(command='help', description='Get help')
]

user_commands = [
    BotCommand(command='start', description='Start'),
    BotCommand(command='metrics', description='My keys statistic'),
    BotCommand(command='new_key', description='Add new key'),
    BotCommand(command='get_key', description='Get credentials for existing key'),
    BotCommand(command='delete_key', description='Delete old key'),
    BotCommand(command='help', description='Get help')
]

group_commands = [
    BotCommand(command='metrics', description='Statistic for all group members'),
    BotCommand(command='help', description='Get help'),
]
