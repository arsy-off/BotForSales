from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthorizationFSM(StatesGroup):
    password = State()


class CurrentStoreFSM(StatesGroup):
    action = State()


class ChangeCurrentStoreFSM(StatesGroup):
    action = State()


class AddOperationFSM(StatesGroup):
    operation_type = State()
    operation_category = State()
    article = State()
    operation_date = State()
    amount = State()
    comment = State()
    confirmation = State()


class EditOperationFSM(StatesGroup):
    operation_type = State()
    operation_category = State()
    article = State()
    operation_date = State()
    show_operations = State()
    confirm_choice = State()
    value_selection = State()

    value_input_subcategory = State()
    value_input_date = State()
    value_input_amount = State()

    confirmation = State()
    action_after = State()
