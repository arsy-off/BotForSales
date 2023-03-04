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
        reply_markup=states.markup_list(op_types, add_cancel_button=False)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.operation_type)
async def add_process_category(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        type_id = int(call.data)
    except ValueError:
        return

    await AddOperationFSM.next()

    categories = await crud.OperationTypeCategoryTable.get_by_operation_type_id(type_id)
    await call.message.answer(
        text='Выберите категорию:',
        reply_markup=states.markup_list(categories)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.operation_category)
async def add_process_article(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        category_id = int(call.data)
    except ValueError:
        return

    await AddOperationFSM.next()

    async with state.proxy() as data:
        data['category_id'] = call.data

    subcategories = await crud.OperationTypeSubcategoryTable.get_by_category_id(category_id)
    await call.message.answer(
        text='Выберите статью:',
        reply_markup=states.markup_list(subcategories)
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.article)
async def add_process_date(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        subcategory_id = int(call.data)
    except ValueError:
        return

    async with state.proxy() as data:
        data['article_id'] = subcategory_id

    await AddOperationFSM.next()
    await call.message.answer(
        text='Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n'
             'Для конкретной даты напишите дату операции в формате: "31.01.2000 15:30"',
        reply_markup=states.skip_state
    )


@dispatcher.message_handler(state=AddOperationFSM.operation_date)
async def add_process_amount(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    async with state.proxy() as data:
        if message.text == 'Продолжить':
            data['operation_date'] = datetime.now()
        elif message.text:
            try:
                data['operation_date'] = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
            except ValueError:
                return await message.answer(text='Проверьте введённый формат и попробуйте ещё раз')

        await AddOperationFSM.next()
        await message.answer(
            text='Введите сумму статьи в формате: "100,00"',
            reply_markup=states.cancel
        )


@dispatcher.message_handler(state=AddOperationFSM.amount)
async def add_process_comment(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

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

    article = await crud.OperationTypeSubcategoryTable.get_by_id(int(data["article_id"]))
    session = await crud.BotAccountSessionTable.get_by_telegram_id(message.from_user.id)

    store = await crud.StoreTable.get_by_id(session.store_id)

    confirmation_text = f'Проверьте введённые данные операции:\n' \
                        f'Магазин: {store.name}\n' \
                        f'Статья: {article.name}\n' \
                        f'Дата: {datetime.strftime(data["operation_date"], "%d.%m.%Y %H:%M")}\n' \
                        f'Сумма: {data["amount"]:.2f}\n' \
                        f'Комментарий: {data["comment"]}'
    # f'Тип: {data["article_id"]}\n' \

    await AddOperationFSM.next()
    await message.answer(
        text=confirmation_text,
        reply_markup=states.confirmation
    )


@dispatcher.callback_query_handler(state=AddOperationFSM.confirmation)
async def add_process_action(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'confirm':
        account_session = await crud.BotAccountSessionTable.get_by_telegram_id(call.from_user.id)
        author = await crud.BotAccountTable.get_by_id(account_session.account_id)
        async with state.proxy() as data:
            await crud.OperationTable.create(
                dt=data['operation_date'],
                subcategory_id=int(data['article_id']),
                amount=float(data['amount']),
                comment=data['comment'],
                author_id=author.employee_id,
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
            subcategories = await crud. \
                OperationTypeSubcategoryTable.get_by_category_id(int(data['category_id']))
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
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )
