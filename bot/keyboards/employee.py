from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


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
