from sqlalchemy import Column, BigInteger, Integer, Text, TIMESTAMP, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Operation(Base):
    __tablename__ = 'operation'

    id = Column(Integer, primary_key=True)
    dt = Column(TIMESTAMP)
    status_id = Column(Integer)
    subcategory_id = Column(Integer)
    author_id = Column(Integer)
    store_id = Column(Integer)
    amount = Column(Numeric)
    comment = Column(Text)


class OperationStatus(Base):
    __tablename__ = 'operation_status'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class OperationType(Base):
    __tablename__ = 'operation_type'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class OperationTypeCategory(Base):
    __tablename__ = 'operation_type_category'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer)
    name = Column(Text)


class OperationTypeSubcategory(Base):
    __tablename__ = 'operation_type_subcategory'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer)
    name = Column(Text)


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    surname = Column(Text)
    name = Column(Text)
    patronymic = Column(Text)
    hiring_date = Column(TIMESTAMP)
    firing_date = Column(TIMESTAMP)
    position_id = Column(Integer)


class BotAccount(Base):
    __tablename__ = 'bot_account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer)
    telegram_id = Column(BigInteger)
    password = Column(Text)
    is_manager = Column(Boolean)


class BotAccountSession(Base):
    __tablename__ = 'bot_account_session'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    telegram_id = Column(BigInteger)
    store_id = Column(Integer)
    active_from = Column(TIMESTAMP)


class Store(Base):
    __tablename__ = 'store'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    type = Column(Text)
    address = Column(Text)
    inn = Column(Integer)
    kkt = Column(Integer)
