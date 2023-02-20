from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dispatcher
from bot.states import AuthorizationFSM
from bot.filters import IsAuthorized
from bot.database import BotAccountTable


START_TEXT = 'Добро пожаловать!\n' \
             '/help - Получить информацию по работе с ботом\n' \
             '/authorize - Авторизоваться в системе'

HELP_TEXT = 'Доступные команды:\n' \
            '/start - Начать работу с ботом\n' \
            '/help - Получить информацию по работе с ботом\n' \
            '/authorize - Авторизоваться в системе'


@dispatcher.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(text=START_TEXT)


@dispatcher.message_handler(commands=['help'])
async def get_help(message: types.Message):
    await message.answer(text=HELP_TEXT)


@dispatcher.message_handler(IsAuthorized(), commands=['authorize'])
async def already_authorized(message: types.Message):
    await message.answer(text='Вы уже авторизованы!')


@dispatcher.message_handler(~IsAuthorized(), commands=['authorize'])
async def authorization(message: types.Message):
    await AuthorizationFSM.password.set()
    await message.answer(text='Для авторизации в системе введите пароль')


@dispatcher.message_handler(state=AuthorizationFSM.password)
async def authorization_process_password(message: types.Message, state: FSMContext):
    account = await BotAccountTable.get_by_password(message.text)
    if account is None:
        await message.answer(text='Пользователь не найден!\nПроверьте пароль и попробуйте ещё раз')
    else:
        await BotAccountTable.update_telegram_id(account, message.from_user.id)
        await state.finish()
        await message.answer(text='Добро пожаловать!')


@dispatcher.message_handler(IsAuthorized(), commands=['main_menu'])
async def authorization_process_password(message: types.Message, state: FSMContext):
    await message.answer(
        text='Что Вы хотите сделать?'
    )