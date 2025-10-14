from fastapi import APIRouter , Depends, FastAPI, HTTPException
from app.services.transaction import create_transaction
from app.models.models import Transaction
from app.settings.database import get_session

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transactions/")
def create_transaction_route(body: Transaction, session=Depends(get_session)):
    response = create_transaction(body, session)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response
