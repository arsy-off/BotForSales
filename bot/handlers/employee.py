from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime
from bot.loader import dispatcher
from bot.filters import IsAuthorized, IsManager
from bot.keyboards import employee
from bot.states import AddOperationFSM, EditOperationFSM
from bot.database import crud


@dispatcher.message_handler(IsAuthorized(), ~IsManager(), commands=['main_menu'])
async def main_menu(message: types.Message):
    await message.answer(
        text='Что Вы хотите сделать?',
        reply_markup=employee.main_menu
    )

# <-- Add -->


@dispatcher.callback_query_handler(lambda call: call.data == 'add')
async def add_article(call: types.CallbackQuery):
    await AddOperationFSM.operation_type.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=employee.get_actual_operation_types(op_types)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.operation_type)
async def add_process_dt(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['operation_type'] = call.data

    await AddOperationFSM.next()
    await call.message.answer(
        text='Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n'
             'Для конкретной даты напишите дату операции в формате: "31.01.2000 15:30"',
        reply_markup=employee.skip_state
    )


@dispatcher.message_handler(state=AddOperationFSM.operation_date)
async def add_process_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Продолжить':
            data['dt'] = datetime.now()
        elif message.text:
            try:
                data['dt'] = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
            except ValueError:
                await message.answer(text='Проверьте введённый формат и попробуйте ещё раз')

    await AddOperationFSM.next()
    # await message.answer(
    #     text='Выберите статью',
    #     reply_markup=
    # )

# <-- Edit -->


@dispatcher.callback_query_handler(lambda call: call.data == 'edit')
async def edit_article(call: types.CallbackQuery):
    await EditOperationFSM.operation_date.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=employee.get_actual_operation_types(op_types)
    )