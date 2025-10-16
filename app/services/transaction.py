
from typing import Optional
from app.services.auth import get_all_information
from app.settings.schemas import Bank_Account, Transaction, User_Bank_Account
from app.services.bank_account import get_account, get_bank_account_id, get_uid
from app.settings.database import get_session, engine, Session
from fastapi import Depends, HTTPException, BackgroundTasks
import time
from app.utils.utils import get_user

def create_transaction(body: Transaction, background_tasks: BackgroundTasks, session: Session, get_user : get_user):
    """ Create a new transaction"""

    get_account_from = get_account(body.iban_from, session)
    get_account_to = get_account(body.iban_to, session)

    if body.iban_from == body.iban_to:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid transaction amount")
    if get_account_from.balance < body.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    if not get_account_from or not get_account_to:
        raise HTTPException(status_code=404, detail="One of the accounts not found")
    if get_account_from.is_closed or get_account_to.is_closed:
        raise HTTPException(status_code=400, detail="One of the accounts is closed")
    
    transaction = Transaction(
        iban_from=body.iban_from,
        iban_to=body.iban_to,
        amount=body.amount,
        action=body.action,
        status="pending"  
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return {"message": "Transaction initiated, pending finalization.", "transaction_id": transaction.id}


def finalize_transaction(id: int):
    """ Tache in background for finalizing a transaction after a delay. """
    with Session(engine) as db_session:
        try:
            time.sleep(5)
            
            transaction = db_session.query(Transaction).filter(Transaction.id == id).first()
            
            if not transaction or transaction.status != "pending":
                return ["error", "Transaction not found or already processed."]

            account_from = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
            account_to = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
            
            if account_from.balance < transaction.amount:
                transaction.status = "failed"
            else:
                account_from.balance -= transaction.amount
                account_to.balance += transaction.amount
                transaction.status = "completed"

            db_session.commit()

        except Exception as e:
            db_session.rollback()
            return ["error", str(e)]  

def get_transaction(id: int, get_user : get_user, session: Session):
    """ Get information about a specific transaction """
    transaction = None
    if id is not None:
        transaction = session.query(Transaction).filter(Transaction.id == id).first()
    if not transaction:
        return {"error": "Transaction not found."}

    return transaction

def get_all_transaction(iban: str,get_user : get_user, session=Depends(get_session)):
    """Get all transactions where the IBAN is either sender or recipient."""
    array = []
    transactions = session.query(Transaction).filter(
        (Transaction.iban_from == iban) | (Transaction.iban_to == iban)
    ).order_by(Transaction.timestamp.desc()).all()

    for transaction in transactions:
        if transaction.iban_from == iban:
            other_iban = transaction.iban_to
        else:
            other_iban = transaction.iban_from
        bank_account = session.query(Bank_Account).filter(Bank_Account.iban == other_iban).first()
        account_name = None
        if bank_account:
            user_bank_account = session.query(User_Bank_Account).filter(
                User_Bank_Account.bank_account_id == bank_account.id
            ).first()
            if user_bank_account:
                account_name = user_bank_account.name
                
        array.append({
            "id": transaction.id,
            "iban_from": transaction.iban_from,
            "iban_to": transaction.iban_to,
            "account_name": account_name,
            "amount": transaction.amount,
            "action": transaction.action,
            "status": transaction.status,
            "timestamp": transaction.timestamp
        })

    return array

def get_iban_from(id: int, get_user : get_user, session=Depends(get_session)):
    """ Get the IBAN of the user's account """
    transaction = get_transaction(id, get_user, session)
    if transaction:
        return transaction.iban_from

def get_iban_to(id: int, session=Depends(get_session)):
    """ Get the IBAN of the beneficiary's account """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.iban_to

def get_amount(id: int, session=Depends(get_session)):
    """ Get the amount of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.amount

def get_action(id: int, session=Depends(get_session)):
    """ Get the action of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.action

def get_date(id: int, session=Depends(get_session)):
    """ Get the date of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.timestamp

def cancel_transaction(id:int , user: get_user , session: Session):
    transaction = get_transaction(id, user, session)
    iban_from = transaction.iban_from
    
    current_user = get_all_information(user, session)
    uid_current_user = current_user["uid"]
    
    uid_user_bank_account = get_uid(iban_from, session)
    
    print(uid_current_user)
    print(uid_user_bank_account)
    
    if uid_current_user != uid_user_bank_account:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if iban_from == transaction.iban_from: 
        if transaction.status == "pending":
            transaction.status = "cancel"
            session.commit()
            session.refresh(transaction)
        if transaction.status == "cancel":
            raise HTTPException(status_code=400, detail="Transaction already canceled")
        
        if transaction.status == "completed":
            raise HTTPException(status_code=400, detail="Transaction already completed")
    else :
        raise HTTPException(status_code=400, detail="Invalid IBAN")
    return transaction
    