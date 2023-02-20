from aiogram import types
from bot.loader import dispatcher
from bot.filters import IsAuthorized, IsManager


@dispatcher.message_handler(IsAuthorized(), IsManager(), commands=['main_menu'])
async def main_menu(message: types.Message):
    await message.answer(
        text='Что Вы хотите сделать?'
    )