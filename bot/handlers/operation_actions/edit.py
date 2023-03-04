import io
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, date
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dispatcher
from bot.filters import HasActiveSession, IsManager
from bot.keyboards import states, common, employee, manager
from bot.states import EditOperationFSM
from bot.database import crud

matplotlib.use('Agg')


@dispatcher.callback_query_handler(HasActiveSession(), lambda call: call.data == 'edit')
async def edit_article(call: types.CallbackQuery):
    await EditOperationFSM.operation_type.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=states.markup_list(op_types, add_cancel_button=False)
    )


@dispatcher.callback_query_handler(state=EditOperationFSM.operation_type)
async def edit_process_category(call: types.CallbackQuery, state: FSMContext):
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

    await EditOperationFSM.next()

    categories = await crud.OperationTypeCategoryTable.get_by_operation_type_id(type_id)
    await call.message.answer(
        text='Выберите категорию:',
        reply_markup=states.markup_list(categories)
    )


@dispatcher.callback_query_handler(state=EditOperationFSM.operation_category)
async def edit_process_article(call: types.CallbackQuery, state: FSMContext):
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

    await EditOperationFSM.next()

    async with state.proxy() as data:
        data['category_id'] = call.data

    subcategories = await crud.OperationTypeSubcategoryTable.get_by_category_id(category_id)
    await call.message.answer(
        text='Выберите статью:',
        reply_markup=states.markup_list(subcategories)
    )


@dispatcher.callback_query_handler(state=EditOperationFSM.article)
async def edit_process_date(call: types.CallbackQuery, state: FSMContext):
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

    await EditOperationFSM.next()
    await call.message.answer(
        text='Укажите на какую дату искать операции в формате: "31.01.2000"\n'
             'Нажмите "Продолжить" чтобы текущая дата подставилась автоматически\n\n'
             'После указания даты будет формироваться список, '
             'это может занять некоторое время',
        reply_markup=states.skip_state
    )


@dispatcher.message_handler(state=EditOperationFSM.operation_date)
async def edit_show_operations(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    async with state.proxy() as data:
        if message.text == 'Продолжить':
            data['operation_date'] = date.today()
        elif message.text:
            try:
                data['operation_date'] = datetime.strptime(message.text, '%d.%m.%Y')
            except ValueError:
                return await message.answer(text='Проверьте введённый формат и попробуйте ещё раз')

        rows = await crud.OperationTable.get_full_on_date(data['operation_date'], data['article_id'])

        if len(rows) == 0:
            return await message.answer(
                text=f'На дату {data["operation_date"].strftime("%d.%m.%Y")} не было найдено операций\n'
                     f'Введите новую дату (Формат: "31.01.2000") или нажмите "Отмена"',
                reply_markup=states.cancel
            )

        op_indexes = {}
        table_rows = []
        for num, row in enumerate(rows, 1):
            op_indexes[num] = row.Operation.id
            table_rows.append([
                num,
                row.Operation.dt.strftime('%d.%m.%Y'),
                row.OperationTypeSubcategory.name,
                row.OperationTypeCategory.name,
                row.OperationStatus.name,
                row.Operation.amount,
                row.Operation.comment,
                row.Employee.surname + row.Employee.name + row.Employee.patronymic
            ])
        data['op_indexes'] = op_indexes

        fig, ax = plt.subplots()
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        table_cols = [
            'Номер', 'Дата операции', 'Комментарий', 'Сумма',
            'Статус', 'Магазин', 'Категория', 'Статья', 'Фамилия', 'Имя', 'Отчество'
        ]
        table = plt.table(
            cellText=table_rows,
            colLabels=table_cols,
            colWidths=[0.3] * len(table_rows[0]),
            loc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(5)
        fig.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=400)
        buf.seek(0)
        buf.name = 'Список операций.png'

        await EditOperationFSM.next()
        await message.answer_document(
            buf
        )
        await message.answer(
            text='Введите номер операции, которой хотите изменить:',
            reply_markup=states.cancel
        )


@dispatcher.message_handler(state=EditOperationFSM.show_operations)
async def edit_confirm_choice(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        row_num = int(message.text)
        async with state.proxy() as data:
            operation_id = data['op_indexes'][row_num]
    except ValueError:
        return await message.answer(text='Пожалуйста, проверьте верно ли введён номер')
    except KeyError:
        return await message.answer(text='Пожалуйста, проверьте верно ли введён номер')

    row = await crud.OperationTable.get_full_by_id(operation_id)
    async with state.proxy() as data:
        data['selected_operation_id'] = operation_id
    await EditOperationFSM.next()

    await message.answer(
        text=f'Это операция, которую Вы загадали?\n'
             f'Категория: {row.OperationTypeCategory.name}\n'
             f'Статья: {row.OperationTypeSubcategory.name}\n'
             f'Дата: {row.Operation.dt.strftime("%d.%m.%Y")}\n'
             f'Статус: {row.OperationStatus.name}\n'
             f'Сумма: {row.Operation.amount}\n'
             f'Комментарий: {row.Operation.comment}\n'
             f'Автор: {row.Employee.surname + row.Employee.name + row.Employee.patronymic}',
        reply_markup=states.operation_choice_confirmation
    )


@dispatcher.callback_query_handler(state=EditOperationFSM.confirm_choice)
async def edit_process_confirmation(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )
    elif call.data == 'change_choice':
        await EditOperationFSM.previous()
        return await call.message.answer(
            text='Введите номер операции, которой хотите изменить:',
            reply_markup=states.cancel
        )
    elif call.data == 'correct_choice':
        await EditOperationFSM.next()
        await call.message.answer(
            text='Выберите что вы хотите изменить:',
            reply_markup=states.operation_value_selection
        )


# <-- subcategory -->


@dispatcher.callback_query_handler(lambda call: call.data == 'change_operation_subcategory',
                                   state=EditOperationFSM.value_selection)
async def edit_process_value_selection_subcategory(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.data.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    subcategories = await crud.OperationTypeSubcategoryTable.get_all()

    await EditOperationFSM.value_input_subcategory.set()
    await call.message.answer(
        text='Выберите новую статью:',
        reply_markup=states.markup_list(subcategories)
    )


@dispatcher.callback_query_handler(state=EditOperationFSM.value_input_subcategory)
async def edit_process_value_input_subcategory(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        subcategory_id = int(call.data)
        async with state.proxy() as data:
            data['change'] = {
                'type': 'subcategory',
                'new_value': subcategory_id
            }

            row = await crud.OperationTable.get_full_by_id(data['selected_operation_id'])

            subcategory = await crud.OperationTypeSubcategoryTable.get_by_id(subcategory_id)
            category = await crud.OperationTypeCategoryTable.get_by_id(subcategory.category_id)

            await EditOperationFSM.confirmation.set()
            await call.message.answer(
                text=f'Обновлённая операция:\n'
                     f'Категория: {category.name}\n'  # <-- Changed attribute
                     f'Статья: {subcategory.name}\n'  # <-- Changed attribute
                     f'Дата: {row.Operation.dt}\n'
                     f'Статус: {row.OperationStatus.name}\n'
                     f'Сумма: {row.Operation.amount}\n'
                     f'Комментарий: {row.Operation.comment}\n'
                     f'Автор: {row.Employee.surname + row.Employee.name + row.Employee.patronymic}',
                reply_markup=states.operation_value_change_confirmation
            )
    except ValueError:
        return


# <-- date -->


@dispatcher.callback_query_handler(lambda call: call.data == 'change_operation_date',
                                   state=EditOperationFSM.value_selection)
async def edit_process_value_selection_date(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.data.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    await EditOperationFSM.value_input_date.set()
    await call.message.answer(
        text='Напишите новую дату операции в формате: "31.01.2000 15:30"',
        reply_markup=states.skip_state
    )


@dispatcher.message_handler(state=EditOperationFSM.value_input_date)
async def edit_process_value_input_date(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    async with state.proxy() as data:
        if message.text == 'Продолжить':
            data['change'] = {
                'type': 'date',
                'new_value': datetime.now()
            }

            row = await crud.OperationTable.get_full_by_id(data['selected_operation_id'])

            await EditOperationFSM.confirmation.set()
            await message.answer(
                text=f'Обновлённая операция:\n'
                     f'Категория: {row.OperationTypeCategory.name}\n'
                     f'Статья: {row.OperationTypeSubcategory.name}\n'
                     f'Дата: {data["change"]["new_value"].strftime("%d.%m.%Y")}\n'  # <-- Changed attribute
                     f'Статус: {row.OperationStatus.name}\n'
                     f'Сумма: {row.Operation.amount}\n'
                     f'Комментарий: {row.Operation.comment}\n'
                     f'Автор: {row.Employee.surname + row.Employee.name + row.Employee.patronymic}',
                reply_markup=states.operation_value_change_confirmation
            )
        elif message.text:
            try:
                dt = datetime.strptime(message.text, '%d.%m.%Y %H:%M')

                data['change'] = {
                    'type': 'date',
                    'new_value': dt
                }

                row = await crud.OperationTable.get_full_by_id(data['selected_operation_id'])

                await EditOperationFSM.confirmation.set()
                await message.answer(
                    text=f'Обновлённая операция:\n'
                         f'Категория: {row.OperationTypeCategory.name}\n'
                         f'Статья: {row.OperationTypeSubcategory.name}\n'
                         f'Дата: {data["change"]["new_value"].strftime("%d.%m.%Y")}\n'  # <-- Changed attribute
                         f'Статус: {row.OperationStatus.name}\n'
                         f'Сумма: {row.Operation.amount}\n'
                         f'Комментарий: {row.Operation.comment}\n'
                         f'Автор: {row.Employee.surname + row.Employee.name + row.Employee.patronymic}',
                    reply_markup=states.operation_value_change_confirmation
                )
            except ValueError:
                return await message.answer(text='Проверьте введённый формат и попробуйте ещё раз')


# <-- amount -->


@dispatcher.callback_query_handler(lambda call: call.data == 'change_operation_amount',
                                   state=EditOperationFSM.value_selection)
async def edit_process_value_selection_amount(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.data.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    await EditOperationFSM.value_input_amount.set()
    await call.message.answer(
        text='Введите новую сумму статьи в формате: "100,00"',
        reply_markup=states.cancel
    )


@dispatcher.message_handler(state=EditOperationFSM.value_input_amount)
async def edit_process_value_input_amount(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        return await message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    try:
        numeric_amount = float(message.text.replace(',', '.'))

        async with state.proxy() as data:
            data['change'] = {
                'type': 'amount',
                'new_value': numeric_amount
            }

            row = await crud.OperationTable.get_full_by_id(data['selected_operation_id'])

            await EditOperationFSM.confirmation.set()
            await message.answer(
                text=f'Обновлённая операция:\n'
                     f'Категория: {row.OperationTypeCategory.name}\n'
                     f'Статья: {row.OperationTypeSubcategory.name}\n'
                     f'Дата: {row.Operation.dt.strftime("%d.%m.%Y")}\n'
                     f'Статус: {row.OperationStatus.name}\n'
                     f'Сумма: {data["change"]["new_value"]:.2}\n'  # <-- Changed attribute
                     f'Комментарий: {row.Operation.comment}\n'
                     f'Автор: {row.Employee.surname + row.Employee.name + row.Employee.patronymic}',
                reply_markup=states.operation_value_change_confirmation
            )

    except ValueError:
        await message.answer(
            text='Проверьте формат вводимой суммы\n'
                 'Формат должен быть следующим: "100,00"'
        )


@dispatcher.callback_query_handler(state=EditOperationFSM.confirmation)
async def edit_process_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cancel':
        await state.finish()
        return await call.message.answer(
            text='Отменено',
            reply_markup=common.to_main_menu
        )

    async with state.proxy() as data:
        operation_id = data['selected_operation_id']
        change_type = data['change']['type']
        change_value = data['change']['new_value']
        if change_type == 'subcategory':
            await crud.OperationTable.update(operation_id, subcategory_id=change_value)
        elif change_type == 'date':
            await crud.OperationTable.update(operation_id, dt=change_value)
        elif change_type == 'amount':
            await crud.OperationTable.update(operation_id, amount=change_value)

    await EditOperationFSM.next()
    await call.message.answer(
        text='Операция успешно изменена',
        reply_markup=states.action_after_confirmation
    )


@dispatcher.callback_query_handler(lambda call: call.data == 'end', state=EditOperationFSM.action_after)
async def edit_process_end(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    account = await crud.BotAccountTable.get_by_telegram_id(call.from_user.id)
    if account.is_manager:
        await call.message.answer(
            text='Что Вы хотите сделать?',
            reply_markup=manager.main_menu
        )
    else:
        await call.message.answer(
            text='Что Вы хотите сделать?',
            reply_markup=employee.main_menu
        )


@dispatcher.callback_query_handler(lambda call: call.data == 'change_another', state=EditOperationFSM.action_after)
async def edit_process_action_after(call: types.CallbackQuery, state: FSMContext):
    await EditOperationFSM.value_selection.set()
    await call.message.answer(
        text='Выберите что вы хотите изменить:',
        reply_markup=states.operation_value_selection
    )
