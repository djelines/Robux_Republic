from fastapi import APIRouter, HTTPException, Depends

from app.models.models import Bank_Account
from app.models.models_create import Bank_Account_create
from app.services.bank_account import create_bank_account
from app.services.user_bank_account import get_all_accounts
from app.settings.database import get_session

router = APIRouter(prefix="/bank_account", tags=["BankAccount"])

@router.post("")
def create_bank_account_route(body: Bank_Account_create, session=Depends(get_session)):
    response = create_bank_account(body, session)

    print(response)

    if response:
        return response

    return HTTPException(status_code=404)

@router.get("/all-bank-accounts")
def get_all_comptes(uid: str, session=Depends(get_session)):
    response = get_all_accounts(uid, session)

    if response:
        return response