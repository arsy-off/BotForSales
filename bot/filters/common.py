from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from bot.database import BotAccountTable


class IsAuthorized(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return bool(await BotAccountTable.get_by_telegram_id(str(message.from_user.id)))


class IsManager(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        account = await BotAccountTable.get_by_telegram_id(str(message.from_user.id))
        return account.is_manager
