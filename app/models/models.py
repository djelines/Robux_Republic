import decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import create_engine
class ActionEnum(str, Enum):
    virement = "virement"
    deposite = "depot"

class User(BaseModel):
    uid: str
    first_name: str
    last_name: str
    address: str

class Auth(BaseModel):
    #uid: str
    email: str
    password: str

class Bank_Account(BaseModel):
    is_principal: bool = False
    is_closed: bool = False
    iban: str
    balance: decimal.Decimal = 0.0

class User_Bank_Account(BaseModel):
    uid: str
    bank_id:int
    bank_account_id: Optional[int] = None
    name: str
    creation_date: datetime

class Transaction(BaseModel):
    iban_from: str
    iban_to: str
    iban_bank_from : Optional[str] = None
    amount: decimal.Decimal
    action:  ActionEnum
    name: str
    status: str = "pending"
    timestamp: datetime = datetime.now()
    if_started: Optional[bool] = False
    is_mail_send: Optional[bool] = False


class Beneficiary(BaseModel):
    name: str
    iban_to: str
    creation_date: datetime = datetime.now()

class Bank_Account_Info(BaseModel):
    id: int
    is_principal: bool
    is_closed: bool
    iban: str
    balance: decimal.Decimal
    name: str
    creation_date: datetime

class Bank_Extern(BaseModel):
    id: int
    name: str
    iban: str
    is_main: bool
    balance: decimal.Decimal

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

def get_db_engine(url="sqlite:////database.db"):
   return create_engine(url)