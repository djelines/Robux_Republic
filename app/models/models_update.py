from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import decimal

from app.models.models import ActionEnum


class User_update(BaseModel):
    """User update model."""
    uid: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None

class Auth_update(BaseModel):
    """Auth update model."""
    uid: str
    email: Optional[str] = None
    password: Optional[str] = None

class Bank_Account_update(BaseModel):
    """Bank Account update model."""
    is_closed: Optional[bool] = None
    balance: Optional[decimal.Decimal] = None

class User_Bank_Account_update(BaseModel):
    """User Bank Account update model."""
    uid: str
    bank_id:Optional[int] = None
    bank_account_id: Optional[int] = None
    name: Optional[str] = None

class Transaction_update(BaseModel):
    """Transaction update model."""
    iban_from: Optional[str] = None
    iban_to: Optional[str] = None
    iban_bank_from : Optional[str] = None
    amount: Optional[decimal.Decimal] = None
    status: Optional[str] = None
    name: Optional[str] = None
    action:  Optional[ActionEnum] = None
    timestamp: Optional[datetime] = None
    if_started: Optional[bool] = False
    is_mail_send: Optional[bool] = False


class Beneficiary_update(BaseModel):
    """Beneficiary update model."""
    name: Optional[str] = None
    iban_to: Optional[str] = None
    
class Bank_Extern_update(BaseModel):
    """Bank Extern update model."""
    id: Optional[int] = None
    is_main: Optional[bool] = None
    name: Optional[str] = None
    iban: Optional[str] = None
    balance: Optional[decimal.Decimal] = None

class UserUpdate(BaseModel):
    """User update model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
