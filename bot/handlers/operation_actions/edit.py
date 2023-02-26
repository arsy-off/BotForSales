from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.loader import dispatcher
from bot.filters import HasActiveSession
from bot.keyboards import states
from bot.states import EditOperationFSM
from bot.database import crud


@dispatcher.callback_query_handler(HasActiveSession(), lambda call: call.data == 'edit')
async def edit_article(call: types.CallbackQuery):
    await EditOperationFSM.operation_date.set()
    op_types = await crud.OperationTypeTable.get_all()

    await call.message.answer(
        text='Выберите тип операции:',
        reply_markup=states.markup_list(op_types)
    )
