from sqlalchemy import Column, Integer, Text, TIMESTAMP, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    dt = Column(TIMESTAMP)
    status_id = Column(Integer)
    type_id = Column(Integer)
    author_id = Column(Integer)
    sum = Column(Numeric)
    comment = Column(Integer)


class OperationStatus(Base):
    __tablename__ = 'operation_statuses'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class OperationType(Base):
    __tablename__ = 'operation_types'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    category_id = Column(Integer)
    subcategory_id = Column(Integer)


class OperationTypeCategory(Base):
    __tablename__ = 'operation_type_categories'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class OperationTypeSubCategory(Base):
    __tablename__ = 'operation_type_subcategories'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    surname = Column(Text)
    name = Column(Text)
    patronymic = Column(Text)
    hiring_date = Column()
    firing_date = Column()
    position_id = Column(Integer)
    account_id = Column(Integer)


class BotAccount(Base):
    __tablename__ = 'bot_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer)
    telegram_id = Column(Text)
    password = Column(Text)


class BotAccountSession(Base):
    __tablename__ = 'bot_account_sessions'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    active_from = Column(TIMESTAMP)
    store_id = Column(Integer)