from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User_update(BaseModel):
    uid: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None

class Auth_update(BaseModel):
    uid: str
    email: Optional[str] = None
    password: Optional[str] = None

class Bank_Account_update(BaseModel):
    is_closed: Optional[bool] = None
    balance: Optional[float] = None

class User_Bank_Account_update(BaseModel):
    uid: str
    bank_account_id: Optional[int] = None
    name: Optional[str] = None

class Transaction_update(BaseModel):
    iban_from: Optional[str] = None
    iban_to: Optional[str] = None
    amount: Optional[float] = None
    action: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None

class Beneficiary_update(BaseModel):
    name: Optional[str] = None
    uid: str
    iban_to: Optional[str] = None
