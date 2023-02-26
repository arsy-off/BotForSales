from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dispatcher
from bot.keyboards import states, common
from bot.states import AddOperationFSM
from bot.database import crud
from bot.filters import HasActiveSession


@dispatcher.callback_query_handler(HasActiveSession(), lambda call: call.data == 'add')
async def add_process_type(call: types.CallbackQuery):
    await AddOperationFSM.operation_type.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=states.markup_list(op_types)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.operation_type)
async def add_process_date(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        return await state.finish()

    async with state.proxy() as data:
        data['operation_type'] = call.data

    await AddOperationFSM.next()
    await call.message.answer(
        text='Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n'
             'Для конкретной даты напишите дату операции в формате: "31.01.2000 15:30"',
        reply_markup=states.skip_state
    )


@dispatcher.message_handler(state=AddOperationFSM.operation_date)
async def add_process_article(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        return await state.finish()

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
        reply_markup=states.markup_list(subcategories)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.article)
async def add_process_amount(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        return await state.finish()

    async with state.proxy() as data:
        data['article'] = call.data

    await AddOperationFSM.next()
    await call.message.answer(
        text='Введите сумму статьи в формате: "100,00"',
        reply_markup=states.cancel
    )


@dispatcher.message_handler(state=AddOperationFSM.amount)
async def add_process_comment(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        return await state.finish()

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
        reply_markup=states.confirmation
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
        reply_markup=states.confirmation
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.confirmation)
async def add_process_action(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'confirm':
        account_session = await crud.BotAccountSessionTable.get_by_telegram_id(call.from_user.id)
        async with state.proxy() as data:
            await crud.OperationTable.create(
                dt=data['operation_date'],
                subcategory_id=int(data['article']),
                amount=float(data['amount']),
                comment=data['comment'],
                author_id=account_session.account_id,
                store_id=account_session.store_id
            )
        await state.finish()
        await call.message.answer(
            text='Операция успешно добавлена',
            reply_markup=common.to_main_menu
        )
    elif call.data == 'change_date':
        await AddOperationFSM.operation_date.set()
        await call.message.answer(
            text='Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n'
                 'Для конкретной даты напишите дату операции в формате: "31.01.2000 15:30"',
            reply_markup=states.skip_state
        )
    elif call.data == 'change_article':
        await AddOperationFSM.article.set()
        async with state.proxy() as data:
            subcategories = await crud.\
                OperationTypeSubcategoryTable.get_by_operation_type_id(int(data['operation_type']))
            await call.message.answer(
                text='Выберите статью:',
                reply_markup=states.markup_list(subcategories)
            )
    elif call.data == 'change_amount':
        await AddOperationFSM.amount.set()
        await call.message.answer(
            text='Введите сумму статьи в формате: "100,00"',
            reply_markup=states.cancel
        )
    elif call.data == 'change_comment':
        await AddOperationFSM.comment.set()
        await call.message.answer(
            text='Введите комментарий к операции:'
        )
    elif call.data == 'cancel':
        await state.finish()
