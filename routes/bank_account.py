from fastapi import APIRouter, HTTPException, Depends

from app.models.models import Bank_Account
from app.models.models_create import Bank_Account_create
from app.services.bank_account import create_bank_account
from app.services.user_bank_account import get_all_accounts
from app.services.bank_account import get_account
from app.settings.database import get_session
from app.utils.utils import get_user

router = APIRouter(prefix="/bank_account", tags=["BankAccount"])

@router.post("")
def create_bank_account_route(body: Bank_Account_create, session=Depends(get_session), get_user= Depends(get_user)):
    response = create_bank_account(body, get_user ,session)

    print(response)

    if response:
        return response

    return HTTPException(status_code=404)

@router.get("/{iban}")
def get_bank_account(iban: str, session=Depends(get_session), get_user= Depends(get_user)):
    response = get_account(iban, get_user ,session)
    if response:
        return response
    return HTTPException(status_code=404)

@router.get("/all-bank-accounts/{uid}")
def get_all_comptes(uid: str, session=Depends(get_session), get_user= Depends(get_user)):
    response = get_all_accounts(uid, get_user,session)

    if response:
        return response