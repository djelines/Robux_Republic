import decimal
from typing import Optional

from pydantic import BaseModel

from app.settings.schemas import Bank_Account, User_Bank_Account


class Bank_Account_create(BaseModel):
    is_principal: Optional[bool] = False
    is_closed: Optional[bool] = False
    iban: Optional[str] = None
    balance: Optional[decimal.Decimal] = decimal.Decimal(0)
    uid: str
    bank_account_id: Optional[int] = None
    name: str
