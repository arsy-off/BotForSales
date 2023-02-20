from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthorizationFSM(StatesGroup):
    password = State()


class AddOperationFSM(StatesGroup):
    operation_type = State()
    operation_date = State()
    article = State()
    amount = State()
    comment = State()
    confirmation = State()
    action = State()


class EditOperationFSM(StatesGroup):
    operation_type = State()
    operation_date = State()
    operation_number = State()
    value_select = State()
    value_input = State()
    confirmation = State()
    action = State()
