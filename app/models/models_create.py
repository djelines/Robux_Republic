import decimal
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.testing import exclude

from app.settings.schemas import Auth, Bank_Account, User_Bank_Account


class Bank_Account_create(BaseModel):
    """Model for Bank_account"""
    is_principal: Optional[bool] = False
    is_closed: Optional[bool] = False
    iban: Optional[str] = None
    balance: Optional[decimal.Decimal] = decimal.Decimal(0)
    uid: Optional[str] = None
    id_bank: Optional[int] = None
    bank_account_id: Optional[int] = None
    name: Optional[str] = None

class Auth_create(BaseModel):
    """Model for Auth"""
    uid: Optional[str] = None
    email: str
    password: str
    first_name: str
    last_name: str
    address: str

class Init_User(BaseModel):
    """Model for initializing User with Auth and Bank_account"""
    auth: Auth_create
    bank_account: Bank_Account_create
