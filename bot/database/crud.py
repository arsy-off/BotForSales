from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.engine import Row
from sqlalchemy import func, update, delete, alias
from bot.loader import async_session
from .models import *


class StoreTable:
    @staticmethod
    async def get_by_id(store_id: int) -> Store:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Store)
                    .where(Store.id == store_id)
                )

                return result.scalars().first()

    @staticmethod
    async def get_all() -> list[Store]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Store))

                return result.scalars().all()


class BotAccountTable:
    @staticmethod
    async def get_by_id(bot_account_id: int) -> BotAccount:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(BotAccount).where(BotAccount.id == bot_account_id))

                return result.scalars().first()

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

    @staticmethod
    async def update(account_id: int, **attrs):
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(BotAccountSession)
                    .where(BotAccountSession.id == account_id)
                    .values(attrs)
                )


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
    async def get_full_by_id(operation_id: int) -> Row[
        Operation,
        OperationStatus,
        Store,
        OperationTypeCategory,
        OperationTypeSubcategory,
        Employee
    ]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(
                        Operation,
                        OperationStatus,
                        Store,
                        OperationTypeCategory,
                        OperationTypeSubcategory,
                        Employee
                    )
                    .where(Operation.id == operation_id)

                    .outerjoin(OperationStatus, Operation.status_id == OperationStatus.id)
                    .outerjoin(Store, Operation.store_id == Store.id)

                    .outerjoin(OperationTypeSubcategory, Operation.subcategory_id == OperationTypeSubcategory.id)
                    .outerjoin(OperationTypeCategory,
                               OperationTypeSubcategory.category_id == OperationTypeCategory.id)
                    .outerjoin(OperationType, OperationTypeCategory.type_id == OperationType.id)

                    .outerjoin(Employee, Operation.author_id == Employee.id)
                    .outerjoin(BotAccount, Employee.id == BotAccount.employee_id)
                )

                return result.first()

    @staticmethod
    async def get_full_on_date(
            date: datetime, subcategory_id: int
    ) -> list[Row[
        Operation,
        OperationStatus,
        Store,
        OperationTypeCategory,
        OperationTypeSubcategory,
        Employee
    ]]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(
                        Operation,
                        OperationStatus,
                        Store,
                        OperationTypeCategory,
                        OperationTypeSubcategory,
                        Employee
                    )
                    .where(
                        (func.date_trunc('day', Operation.dt) == date)
                        & (Operation.subcategory_id == subcategory_id)
                    )

                    .outerjoin(OperationStatus, Operation.status_id == OperationStatus.id)
                    .outerjoin(Store, Operation.store_id == Store.id)

                    .outerjoin(OperationTypeSubcategory, Operation.subcategory_id == OperationTypeSubcategory.id)
                    .outerjoin(OperationTypeCategory,
                               OperationTypeSubcategory.category_id == OperationTypeCategory.id)
                    .outerjoin(OperationType, OperationTypeCategory.type_id == OperationType.id)

                    .outerjoin(Employee, Operation.author_id == Employee.id)
                    .outerjoin(BotAccount, Employee.id == BotAccount.employee_id)
                )

                return result.all()

    @staticmethod
    async def update(operation_id: int, **attrs) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(Operation)
                    .where(Operation.id == operation_id)
                    .values(attrs)
                )

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
                result = await session.execute(
                    select(OperationType)
                    .order_by(OperationType.name)
                )

                return result.scalars().all()


class OperationTypeCategoryTable:
    @staticmethod
    async def get_by_id(operation_type_id: int) -> OperationTypeCategory:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeCategory).where(OperationTypeCategory.id == operation_type_id)
                )

                return result.scalars().first()

    @staticmethod
    async def get_all() -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeCategory)
                    .order_by(OperationTypeCategory.name)
                )

                return result.scalars().all()

    @staticmethod
    async def get_by_operation_type_id(type_id: int) -> list[OperationTypeCategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeCategory)
                    .where(OperationTypeCategory.type_id == type_id)
                    .order_by(OperationTypeCategory.name)
                )

                return result.scalars().all()


class OperationTypeSubcategoryTable:
    @staticmethod
    async def get_by_id(subcategory_id: int) -> OperationTypeSubcategory:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .where(OperationTypeSubcategory.id == subcategory_id)
                    .order_by(OperationTypeSubcategory.name)
                )

                return result.scalars().first()

    @staticmethod
    async def get_all() -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .order_by(OperationTypeSubcategory.name)
                )

                return result.scalars().all()

    @staticmethod
    async def get_by_category_id(category_id: int) -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .where(OperationTypeSubcategory.category_id == category_id)
                    .order_by(OperationTypeSubcategory.name)
                )

                return result.scalars().all()

    @staticmethod
    async def get_by_operation_type_id(type_id: int) -> list[OperationTypeSubcategory]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(OperationTypeSubcategory)
                    .join(OperationTypeCategory, OperationTypeSubcategory.category_id == OperationTypeCategory.id)
                    .where(OperationTypeCategory.type_id == type_id)
                    .order_by(OperationTypeSubcategory.name)
                )

                return result.scalars().all()
