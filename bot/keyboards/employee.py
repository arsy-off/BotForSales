from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.database.models import *


main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить запись',
                callback_data='add'
            )
        ],
        [
            InlineKeyboardButton(
                text='Редактировать запись',
                callback_data='edit'
            )
        ]
    ]
)

skip_state = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Продолжить')]],
    resize_keyboard=True
)


def get_actual_operation_types(op_types: list[OperationType]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=op_type.name, callback_data=op_type.id)] for op_type in op_types]
    )


def get_actual_type_categories(
        op_types: list[OperationTypeCategory | OperationTypeSubcategory]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=op_type.name, callback_data=op_type.id)] for op_type in op_types]
    )


confirmation = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text='Всё ок!')
        ]
    ]
)