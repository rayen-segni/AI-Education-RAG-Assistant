import psycopg
from contextlib import asynccontextmanager
from config import settings



@asynccontextmanager
async def get_conn():

    async with await psycopg.AsyncConnection.connect(settings.database_url()) as conn:
        yield conn

