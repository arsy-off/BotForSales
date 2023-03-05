from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.environ['API_TOKEN'])
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

engine = create_async_engine(
    f'postgresql+asyncpg://{os.environ["DATABASE_USER"]}:{os.environ["DATABASE_PASSWORD"]}'
    f'@{os.environ["DATABASE_HOST"]}:{os.environ["DATABASE_PORT"]}/{os.environ["DATABASE_NAME"]}',
    echo=False
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
