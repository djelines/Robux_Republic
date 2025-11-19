from app.models.models_create import Bank_Account_create
from app.services import user_bank_account
from app.services.user_bank_account import create_user_bank_account, get_all_accounts, get_uid, \
    get_all_bank_account_sql, get_bank_id
from app.settings.schemas import Bank_Account as Bank_Account_SQLModel
from app.models.models import Bank_Account as Bank_AccountModel, Bank_Account
from app.settings.schemas import User_Bank_Account,Bank_Extern
from app.settings.database import get_session
from fastapi import Depends, HTTPException

def get_account_bank_extern(iban: str , session:Depends(get_session)) -> Bank_Account:
    """ Get a specific bank account by its IBAN """
    return session.query(Bank_Extern).filter(Bank_Extern.iban == iban).first()

def get_main_bank_extern(session:Depends(get_session)) -> Bank_Account:
    """ Get the main robux bank account """
    print("Getting main bank extern")
    return session.query(Bank_Extern).filter(Bank_Extern.is_main == True).first()