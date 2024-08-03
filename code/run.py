import asyncio

from db_models import create_tables

# Run this file to run bot
create_tables()

from bot import run_bot

asyncio.run(run_bot())
