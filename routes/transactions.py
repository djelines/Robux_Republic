from fastapi import APIRouter, BackgroundTasks , Depends, FastAPI, HTTPException
from app.services.transaction import create_transaction, get_all_transaction ,get_transaction
from app.models.models import Transaction
from app.settings.database import get_session
from app.utils.utils import get_user



router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transactions/")
def create_transaction_route(body: Transaction, background_tasks: BackgroundTasks, session=Depends(get_session), get_user = Depends(get_user)):
    response = create_transaction(body, background_tasks, session , get_user)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response

@router.get("/transactions/{iban}")
def get_all_transactions_route(iban: str, session=Depends(get_session), get_user = Depends(get_user)):
    return get_all_transaction(iban, session , get_user)

@router.get("/transaction/{id}")
def get_transaction_route(id: int, session=Depends(get_session), get_user = Depends(get_user)):
    response = get_transaction(id, session,get_user)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response
