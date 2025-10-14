from fastapi import APIRouter, BackgroundTasks , Depends, FastAPI, HTTPException
from app.services.transaction import create_transaction, get_all_transaction ,get_transaction
from app.models.models import Transaction
from app.settings.database import get_session



router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transactions/")
def create_transaction_route(body: Transaction, background_tasks: BackgroundTasks, session=Depends(get_session)):
    response = create_transaction(body, background_tasks, session)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response

@router.get("/transactions/{iban}")
def get_all_transactions_route(iban: str, session=Depends(get_session)):
    return get_all_transaction(iban, session)

@router.get("/transaction/{id}")
def get_transaction_route(id: int, session=Depends(get_session)):
    response = get_transaction(id, session)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response
