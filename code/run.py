import asyncio
from db_models import create_tables

from bot import run_bot

# Run this file to run bot
create_tables()
asyncio.run(run_bot())
