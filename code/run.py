import asyncio

from bot import run_bot
from db_models import create_tables

# Run this file to run bot
create_tables()
asyncio.run(run_bot())
