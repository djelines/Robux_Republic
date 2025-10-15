import decimal
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.testing import exclude

from app.settings.schemas import Auth, Bank_Account, User_Bank_Account


class Bank_Account_create(BaseModel):
    is_principal: Optional[bool] = False
    is_closed: Optional[bool] = False
    iban: Optional[str] = None
    balance: Optional[decimal.Decimal] = decimal.Decimal(0)
    uid: str
    bank_account_id: Optional[int] = None
    name: str
    
class Auth_create(BaseModel):
    uid: str
    email: str
    password: str
    first_name: str
    last_name: str
    address: str

class Init_User(BaseModel):
    auth: Auth_create
    bank_account: Bank_Account_create