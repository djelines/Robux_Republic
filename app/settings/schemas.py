from datetime import datetime
from typing import Optional
from fastapi import FastAPI , Depends
from sqlmodel import SQLModel , Field
import decimal


class User (SQLModel , table=True):
    uid : str = Field(index=True, unique=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    address : str
    
class Auth (SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid : str = Field(index=True, unique=True , foreign_key="user.uid")
    email : str = Field(index=True, unique=True)
    password : str
    
class Bank_Account (SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_principal : bool = Field(default=False)
    is_closed : bool = Field(default=False)
    iban : str = Field(index=True, unique=True)
    balance : decimal.Decimal = Field(default=0.0)
    
class User_Bank_Account (SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bank_id:int = Field(index=True, foreign_key="Bank_Extern_update.id")
    uid : str = Field(index=True , foreign_key="user.uid")
    bank_account_id : int = Field(index=True, foreign_key="bank_account.id")
    name : str = Field(index=True)
    creation_date: datetime = Field(default_factory=datetime.now)

class Transaction (SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    iban_from : str = Field(index=True, foreign_key="bank_account.iban")
    iban_to : str = Field(index=True, foreign_key="bank_account.iban")
    amount : decimal.Decimal
    action : str
    status : str = Field(default="pending")
    timestamp : datetime = Field(default_factory=datetime.now)
    
class Beneficiary (SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(index=True)
    uid : str = Field(index=True , foreign_key="user.uid")
    iban_to : str = Field(index=True, foreign_key="bank_account.iban")
    creation_date: datetime = Field(default_factory=datetime.now)
    
class Bank_Extern(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_main: bool = Field(default=False)
    name: str
    iban: str = Field(index=True, unique=True)
    balance: decimal.Decimal = Field(default=999999999999.0 , index=True)