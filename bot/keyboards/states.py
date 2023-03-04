from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.database.models import *


def markup_list(
        items: list[OperationType | OperationTypeCategory | OperationTypeSubcategory | Store],
        add_cancel_button=True
) -> InlineKeyboardMarkup:
    items_markup = [[InlineKeyboardButton(text=item.name, callback_data=item.id)] for item in items]
    if add_cancel_button:
        items_markup += [[InlineKeyboardButton(text='Отмена', callback_data='cancel')]]

    return InlineKeyboardMarkup(inline_keyboard=items_markup)


skip_state = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Продолжить')
        ],
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

cancel = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirmation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Подтвердить',
                callback_data='confirm'
            )
        ],
        [
            InlineKeyboardButton(
                text='Изменить дату',
                callback_data='change_date'
            )
        ],
        [
            InlineKeyboardButton(
                text='Изменить статью',
                callback_data='change_article'
            )
        ],
        [
            InlineKeyboardButton(
                text='Изменить сумму',
                callback_data='change_amount'
            )
        ],
        [
            InlineKeyboardButton(
                text='Изменить комментарий',
                callback_data='change_comment'
            )
        ],
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel'
            )
        ]
    ]
)

operation_choice_confirmation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Операция выбрана корректно',
                callback_data='correct_choice'
            )
        ],
        [
            InlineKeyboardButton(
                text='Выбрать операцию с другим номером',
                callback_data='change_choice'
            )
        ],
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel'
            )
        ]
    ]
)

operation_value_selection = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Статью',
                callback_data='change_operation_subcategory'
            )
        ],
        [
            InlineKeyboardButton(
                text='Дату',
                callback_data='change_operation_date'
            )
        ],
        [
            InlineKeyboardButton(
                text='Сумму',
                callback_data='change_operation_amount'
            )
        ]
    ]
)

operation_value_change_confirmation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Подтвердить',
                callback_data='confirm'
            )
        ],
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel'
            )
        ]
    ]
)

action_after_confirmation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Изменить ещё атрибут',
                callback_data='change_another'
            )
        ],
        [
            InlineKeyboardButton(
                text='Закончить',
                callback_data='end'
            )
        ]
    ]
)
