from sqlalchemy.future import select
from bot.loader import async_session
from .models import *


class BotAccountTable:
    @staticmethod
    async def get_by_telegram_id(telegram_id: str) -> BotAccount:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(BotAccount).where(BotAccount.telegram_id == telegram_id))

                return result.scalars().first()

    @staticmethod
    async def get_by_password(password: str) -> BotAccount:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(BotAccount).where(BotAccount.password == password))

                return result.scalars().first()

    @staticmethod
    async def update_telegram_id(account: BotAccount, telegram_id: str) -> None:
        async with async_session() as session:
            async with session.begin():
                account.telegram_id = str(telegram_id)
                session.add(account)


class OperationTypeTable:
    @staticmethod
    async def get_by_id(type_id: int) -> OperationType:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationType)
                    .where(OperationType.id == type_id)
                )

                return result.scalars().first()

    @staticmethod
    async def get_all() -> list[OperationType]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(OperationType))

                return result.scalars().all()


class OperationTypeSubcategoryTable:
    @staticmethod
    async def get_by_id(subcategory_id: int) -> OperationTypeSubcategory:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .where(OperationTypeSubcategory.id == subcategory_id)
                )

                return result.scalars().first()

    @staticmethod
    async def get_all() -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(OperationTypeSubcategory))

                return result.scalars().all()

    @staticmethod
    async def get_by_operation_type_id(type_id: int) -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .join(OperationTypeCategory, OperationTypeSubcategory.category_id == OperationTypeCategory.id)
                    .where(OperationTypeCategory.type_id == type_id)
                )

                return result.scalars().all()
