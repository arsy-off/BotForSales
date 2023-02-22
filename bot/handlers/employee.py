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


@dispatcher.callback_query_handler(IsAuthorized(), ~IsManager(), lambda call: call.data == 'main_menu')
async def call_main_menu(call: types.CallbackQuery):
    await call.message.answer(
        text='Что Вы хотите сделать?',
        reply_markup=employee.main_menu
    )

# <-- Add -->


@dispatcher.callback_query_handler(lambda call: call.data == 'add')
async def add_process_type(call: types.CallbackQuery):
    await AddOperationFSM.operation_type.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=employee.get_actual_operation_types(op_types)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.operation_type)
async def add_process_date(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['operation_type'] = call.data

    await AddOperationFSM.next()
    await call.message.answer(
        text='Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n'
             'Для конкретной даты напишите дату операции в формате: "31.01.2000 15:30"',
        reply_markup=employee.skip_state
    )


@dispatcher.message_handler(state=AddOperationFSM.operation_date)
async def add_process_article(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Продолжить':
            data['operation_date'] = datetime.now()
        elif message.text:
            try:
                data['operation_date'] = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
            except ValueError:
                await message.answer(text='Проверьте введённый формат и попробуйте ещё раз')

    await AddOperationFSM.next()

    subcategories = await crud.OperationTypeSubcategoryTable.get_by_operation_type_id(int(data['operation_type']))
    await message.answer(
        text='Выберите статью:',
        reply_markup=employee.get_actual_type_categories(subcategories)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.article)
async def add_process_amount(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['article'] = call.data

    await AddOperationFSM.next()
    await call.message.answer(
        text='Введите сумму статьи в формате: "100,00"'
    )


@dispatcher.message_handler(state=AddOperationFSM.amount)
async def add_process_comment(message: types.Message, state: FSMContext):
    try:
        numeric_amount = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            data['amount'] = numeric_amount

        await AddOperationFSM.next()
        await message.answer(
            text='Введите комментарий к операции:'
        )
    except ValueError:
        await message.answer(
            text='Проверьте формат вводимой суммы\n'
                 'Формат должен быть следующим: "100,00"'
        )


@dispatcher.message_handler(state=AddOperationFSM.comment)
async def add_process_confirmation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text

    type_obj = await crud.OperationTypeTable.get_by_id(int(data["operation_type"]))
    article_obj = await crud.OperationTypeSubcategoryTable.get_by_id(int(data["article"]))

    confirmation_text = f'Проверьте введённые данные операции:\n' \
                        f'Тип: {type_obj.name}\n' \
                        f'Дата: {datetime.strftime(data["operation_date"], "%d.%m.%Y %H:%M")}\n' \
                        f'Статья: {article_obj.name}\n' \
                        f'Сумма: {data["amount"]:.2f}\n' \
                        f'Комментарий: {data["comment"]}'

    await AddOperationFSM.next()
    await message.answer(
        text=confirmation_text,
        reply_markup=employee.confirmation
    )

# <-- Edit -->


@dispatcher.callback_query_handler(lambda call: call.data == 'edit')
async def edit_article(call: types.CallbackQuery):
    await EditOperationFSM.operation_date.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=employee.get_actual_operation_types(op_types)
    )