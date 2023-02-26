from datetime import datetime
from sqlalchemy.future import select
from bot.loader import async_session
from .models import *


class StoreTable:
    @staticmethod
    async def get_all() -> list[Store]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Store))

                return result.scalars().all()


class BotAccountTable:
    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> BotAccount:
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
    async def update_telegram_id(account: BotAccount, telegram_id: int) -> None:
        async with async_session() as session:
            async with session.begin():
                account.telegram_id = telegram_id
                session.add(account)


class BotAccountSessionTable:
    @staticmethod
    async def create(account_id: int, store_id: int, telegram_id: int, active_from=datetime.now()) -> None:
        async with async_session() as session:
            async with session.begin():
                session.add(
                    BotAccountSession(
                        account_id=account_id,
                        telegram_id=telegram_id,
                        store_id=store_id,
                        active_from=active_from
                    )
                )

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> BotAccountSession:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(BotAccountSession)
                    .where(BotAccountSession.telegram_id == telegram_id)
                )

                return result.scalars().first()


class OperationTable:
    @staticmethod
    async def create(
            dt: datetime,
            subcategory_id: int,
            amount: float,
            author_id: int = None,
            store_id: int = None,
            status_id: int = 1,
            comment: str = ''
    ) -> None:
        async with async_session() as session:
            async with session.begin():
                session.add(
                    Operation(
                        dt=dt,
                        status_id=status_id,
                        store_id=store_id,
                        author_id=author_id,
                        subcategory_id=subcategory_id,
                        amount=amount,
                        comment=comment
                    )
                )

    @staticmethod
    async def get() -> Operation:
        pass

    @staticmethod
    async def get_on_date(date: datetime, operation_type_id: int = None) -> list[Operation]:
        pass

    @staticmethod
    async def update(operation_id: int) -> None:
        pass

    @staticmethod
    async def delete(operation_id: int) -> None:
        pass


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
