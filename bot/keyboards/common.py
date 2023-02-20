from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


authorisation_success = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        ]
    ]
)