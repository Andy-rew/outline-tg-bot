import asyncio

from code.admin.admin_bot import run_admin_bot
from code.outline import get_outline_client

# from code.user.user import run_user_bot
# from code.group.group import run_group_bot

client = get_outline_client()

asyncio.run(run_admin_bot())
# asyncio.run(run_user_bot())
# asyncio.run(run_group_bot())
