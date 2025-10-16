from fastapi import APIRouter, BackgroundTasks , Depends, FastAPI, HTTPException
from app.services.transaction import cancel_transaction, create_transaction, get_all_transaction ,get_transaction
from sqlalchemy.orm import Session
from app.models.models import Transaction
from app.settings.database import get_session
from app.utils.utils import get_user



router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transactions/")
def create_transaction_route(body: Transaction, background_tasks: BackgroundTasks, session: Session = Depends(get_session), get_user: dict = Depends(get_user)):
    response = create_transaction(body, background_tasks, session, get_user)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response

@router.get("/transactions/{iban}")
def get_all_transactions_route(iban: str, session=Depends(get_session), get_user = Depends(get_user),
                               group_by: str = None):
    return get_all_transaction(iban , group_by, get_user, session)

@router.get("/transaction/{id}")
def get_transaction_route(id: int, session=Depends(get_session), get_user = Depends(get_user)):
    response = get_transaction(id,get_user, session)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response

@router.post("/transaction/{id}/cancel")
def cancel_transaction_route(id: int, get_user = Depends(get_user), session=Depends(get_session)):
    return cancel_transaction(id, get_user, session)