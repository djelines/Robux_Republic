from itertools import groupby
from typing import List

from fastapi import Depends
from sqlmodel import Session

from app.models.models import User_Bank_Account as User_Bank_Account_Models, Bank_Account_Info
from app.settings.database import get_session
from app.settings.schemas import User_Bank_Account, Bank_Account,Bank_Extern
from app.utils.utils import get_user
from app.settings.config import BANK_NAME


def create_user_bank_account(body: User_Bank_Account_Models, session = Depends(get_session)) -> User_Bank_Account:
    user_bank_account = User_Bank_Account(**body.model_dump())
    session.add(user_bank_account)

    return user_bank_account


def get_account():
    """ Get information about a specific user bank account """
    
    pass

def get_all_accounts(uid: str, query_params_group_by: str, get_user : get_user, session = Depends(get_session)) -> List[Bank_Account_Info]:
    """ Get all information about user bank accounts """
    resultArray = []

    user_bank_accounts = session.query(User_Bank_Account).filter(User_Bank_Account.uid == uid).order_by(User_Bank_Account.creation_date.asc()).all()

    for user_bank_account in user_bank_accounts:
        bank_account = session.query(Bank_Account).filter(Bank_Account.id == user_bank_account.bank_account_id and 
                                                          Bank_Account.is_closed == False).first()
        resultArray.append(Bank_Account_Info(
            id=user_bank_account.id,
            name=user_bank_account.name,
            is_principal=bank_account.is_principal,
            is_closed=bank_account.is_closed,
            creation_date=user_bank_account.creation_date,
            balance=bank_account.balance,
            iban=bank_account.iban,
        ))

    if query_params_group_by == "is_principal":
        resultArray = [{"principal_account" if is_principal else "secondary_account": list(bank_account_array) for is_principal, bank_account_array in groupby(resultArray, key=lambda t: t.is_principal)}]
    elif query_params_group_by and query_params_group_by != "is_principal":
        resultArray = [{query_params_group_by: list(bank_account_array) for query_params_group_by, bank_account_array in groupby(resultArray, key=lambda t: getattr(t, query_params_group_by))}]

    return resultArray

def get_all_bank_account_sql(uid: str, get_user : get_user, session=Depends(get_session)) -> List[Bank_Account]:

    user_bank_accounts = session.query(User_Bank_Account).filter(User_Bank_Account.uid == uid).order_by(User_Bank_Account.creation_date.asc()).all()

    all_bank_accounts = []

    for user_bank_account in user_bank_accounts:
        bank_account = session.query(Bank_Account).filter(Bank_Account.id == user_bank_account.bank_account_id and
                                                          Bank_Account.is_closed == False).first()
        all_bank_accounts.append(bank_account)

    return all_bank_accounts

def get_account_id():
    pass

def get_uid(iban : str, session : Session = Depends(get_session)):
    
    account_id = session.query(Bank_Account.id).filter(Bank_Account.iban == iban).scalar()
    uid = session.query(User_Bank_Account.uid).filter(User_Bank_Account.bank_account_id == account_id).scalar()
    return uid

def get_name():
    pass

def get_bank_id( session : Session = Depends(get_session) ):
    return session.query(Bank_Extern.id).filter(Bank_Extern.name == BANK_NAME).scalar()

