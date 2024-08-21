import asyncio

from code.admin.admin_bot import run_admin_bot

from code.user.user_bot import run_user_bot
from code.group.group_bot import run_group_bot

asyncio.run(run_admin_bot())
asyncio.run(run_user_bot())
asyncio.run(run_group_bot())
