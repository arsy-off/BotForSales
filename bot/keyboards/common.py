from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

cancel = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


to_main_menu = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        ]
    ]
)
