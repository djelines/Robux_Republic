from fastapi import APIRouter, HTTPException, Depends

from app.models.models import Bank_Account
from app.models.models_create import Bank_Account_create
from app.services.bank_account import create_bank_account, close_account, get_all
from app.services.bank_extern import get_main_bank_extern
from app.services.user_bank_account import get_all_accounts
from app.services.bank_account import get_account
from app.settings.database import get_session
from app.utils.utils import get_user

router = APIRouter(prefix="/bank_account", tags=["BankAccount"])


    
@router.get("/mother-bank-account")
def get_mother_bank_account(session=Depends(get_session), get_user= Depends(get_user)):
    """get the main bank extern account"""
    response = get_main_bank_extern(session)

    if response:
        return response
    else:
        raise HTTPException(status_code=404)

@router.get("/{iban}")
def get_bank_account(iban: str, session=Depends(get_session), get_user= Depends(get_user)):
    """get a bank account based on iban"""
    response = get_account(iban, get_user ,session)
    if response:
        return response
    return HTTPException(status_code=404)

@router.get("/all-bank-accounts/{uid}")
def get_all_bank_account_of_user(uid: str, group_by: str = None, session=Depends(get_session), get_user= Depends(get_user)):
    """get all bank accounts of a user based on uid"""
    response = get_all_accounts(uid, group_by, get_user,session)

    if response:
        return response

@router.post("")
def create_bank_account_route(body: Bank_Account_create, session=Depends(get_session), get_user= Depends(get_user)):
    """create a bank account for a user"""
    response = create_bank_account(body, get_user ,session)

    print(response)

    if response:
        return response

    return HTTPException(status_code=404)

@router.put("/close/{iban}")
def close_bank_account(iban: str, session=Depends(get_session), get_user = Depends(get_user)):
    """close a bank account based on iban"""
    return close_account(iban, get_user, session)


