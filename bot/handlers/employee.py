from aiogram import types
from bot.loader import dispatcher
from bot.filters import IsAuthorized, IsManager
from bot.keyboards import employee


@dispatcher.message_handler(IsAuthorized(), ~IsManager(), commands=['main_menu'])
async def main_menu(message: types.Message):
    await message.answer(
        text='Что Вы хотите сделать?',
        reply_markup=employee.main_menu
    )


@dispatcher.callback_query_handler(IsAuthorized(), ~IsManager(), lambda call: call.data == 'main_menu')
async def main_menu_cb(call: types.CallbackQuery):
    await call.message.answer(
        text='Что Вы хотите сделать?',
        reply_markup=employee.main_menu
    )
