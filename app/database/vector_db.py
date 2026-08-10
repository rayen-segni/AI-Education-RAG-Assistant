import psycopg
from contextlib import asynccontextmanager
from app.config import settings



@asynccontextmanager
async def get_conn():

    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn: # type: ignore
        yield conn

