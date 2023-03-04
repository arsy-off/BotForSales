from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dispatcher
from bot.states import AuthorizationFSM, CurrentStoreFSM, ChangeCurrentStoreFSM
from bot.filters import IsAuthorized, IsManager, HasActiveSession
from bot.database import BotAccountTable
from bot.keyboards import common, manager, employee, states
from bot.database import crud

START_TEXT_UNAUTHORIZED = 'Добро пожаловать!\n' \
                          '/help - Получить информацию по работе с ботом\n' \
                          '/authorize - Авторизоваться в системе'

START_TEXT_AUTHORIZED = 'Добро пожаловать!\n' \
                        '/help - Получить информацию по работе с ботом\n' \
                        '/main_menu - Главное меню'

HELP_TEXT_UNAUTHORIZED = 'Доступные команды:\n' \
                         '/start - Начать работу с ботом\n' \
                         '/help - Получить информацию по работе с ботом\n' \
                         '/authorize - Авторизоваться в системе'

HELP_TEXT_AUTHORIZED = 'Доступные команды:\n' \
                       '/start - Начать работу с ботом\n' \
                       '/help - Получить информацию по работе с ботом\n' \
                       '/main_menu - Главное меню'


@dispatcher.message_handler(~IsAuthorized(), commands=['start'])
async def start(message: types.Message):
    await message.answer(text=START_TEXT_UNAUTHORIZED)


@dispatcher.message_handler(IsAuthorized(), commands=['start'])
async def start(message: types.Message):
    await message.answer(text=START_TEXT_AUTHORIZED)


@dispatcher.message_handler(~IsAuthorized(), commands=['help'])
async def get_help_unauthorized(message: types.Message):
    await message.answer(text=HELP_TEXT_UNAUTHORIZED)


@dispatcher.message_handler(IsAuthorized(), commands=['help'])
async def get_help_authorized(message: types.Message):
    await message.answer(
        text=HELP_TEXT_AUTHORIZED,
        reply_markup=common.to_main_menu
    )


@dispatcher.message_handler(IsAuthorized(), commands=['authorize'])
async def already_authorized(message: types.Message):
    await message.answer(
        text='Вы уже авторизованы!',
        reply_markup=common.to_main_menu
    )


@dispatcher.message_handler(~IsAuthorized(), commands=['authorize'])
async def authorization(message: types.Message):
    await AuthorizationFSM.password.set()
    await message.answer(
        text='Для авторизации в системе введите пароль',
        reply_markup=common.cancel
    )


@dispatcher.message_handler(state=AuthorizationFSM.password)
async def authorization_process_password(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        return await state.finish()

    account = await BotAccountTable.get_by_password(message.text)
    if account is None:
        await message.answer(
            text='Пользователь не найден!\nПроверьте пароль и попробуйте ещё раз',
            reply_markup=common.cancel
        )
    else:
        await BotAccountTable.update_telegram_id(account, message.from_user.id)
        await state.finish()

        if account.is_manager:
            await message.answer(
                text='Добро пожаловать!\nЧто Вы хотите сделать?',
                reply_markup=manager.main_menu
            )
        else:
            await message.answer(
                text='Добро пожаловать!\nЧто Вы хотите сделать?',
                reply_markup=employee.main_menu
            )


# <-- Current session store -->

@dispatcher.message_handler(IsAuthorized(), ~IsManager(), ~HasActiveSession())
async def set_current_store(message: types.Message):
    await CurrentStoreFSM.action.set()
    stores = await crud.StoreTable.get_all()
    await message.answer(
        text='Выберите магазин на текущий день:',
        reply_markup=states.markup_list(stores)
    )


@dispatcher.callback_query_handler(IsAuthorized(), ~IsManager(), ~HasActiveSession())
async def set_current_store_cb(call: types.CallbackQuery):
    await CurrentStoreFSM.action.set()
    stores = await crud.StoreTable.get_all()
    await call.message.answer(
        text='Выберите магазин на текущий день:',
        reply_markup=states.markup_list(stores)
    )


@dispatcher.callback_query_handler(state=CurrentStoreFSM.action)
async def set_process_current_store(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    account = await crud.BotAccountTable.get_by_telegram_id(call.from_user.id)
    await crud.BotAccountSessionTable.create(
        account_id=account.id,
        telegram_id=account.telegram_id,
        store_id=int(call.data)
    )
    await state.finish()
    await call.message.answer(
        text='Магазин выбран успешно',
        reply_markup=employee.main_menu
    )


@dispatcher.callback_query_handler(IsAuthorized(), ~IsManager(), lambda call: call.data == 'change_store')
async def change_current_store(call: types.CallbackQuery):
    await ChangeCurrentStoreFSM.action.set()
    stores = await crud.StoreTable.get_all()
    await call.message.answer(
        text='Выберите магазин:',
        reply_markup=states.markup_list(stores)
    )


@dispatcher.callback_query_handler(state=ChangeCurrentStoreFSM.action)
async def change_process_current_store(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    session = await crud.BotAccountSessionTable.get_by_telegram_id(call.from_user.id)
    await crud.BotAccountSessionTable.update(
        account_id=session.id,
        store_id=int(call.data)
    )
    await state.finish()
    await call.message.answer(
        text='Магазин обновлён успешно',
        reply_markup=employee.main_menu
    )
