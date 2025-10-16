from itertools import groupby
from typing import Optional

from app.models.models import ActionEnum
from app.services.auth import get_all_information
from app.services.bank_extern import get_account_bank_extern
from app.settings.schemas import Bank_Account, Transaction, User_Bank_Account
from app.services.bank_account import get_account, get_bank_account_id, get_uid
from app.settings.database import get_session, engine, Session
from fastapi import Depends, HTTPException, BackgroundTasks
import time
from app.utils.utils import get_user


######################
#     Create Transaction
####################
def create_transaction(body: Transaction, background_tasks: BackgroundTasks, session: Session, get_user: get_user):
    """ Create a new transaction"""
    get_account_to = get_account(body.iban_to, get_user, session)
    if body.iban_from == body.iban_to:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid transaction amount")

    if body.action == ActionEnum.virement and "TowerTrump" not in body.iban_from:
        get_account_from = get_account(body.iban_from, get_user, session)
        if get_account_from.balance < body.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        if get_account_from.is_closed or get_account_to.is_closed:
            raise HTTPException(status_code=400, detail="One of the accounts is closed")
        if not get_account_from or not get_account_to:
            raise HTTPException(status_code=404, detail="One of the accounts not found")

    elif body.action == ActionEnum.deposite:
        if body.iban_bank_from and body.iban_bank_from != "string":
            get_account_bank_from = get_account_bank_extern(body.iban_bank_from, session)
            if get_account_bank_from.balance < body.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            if get_account_to.is_closed:
                raise HTTPException(status_code=400, detail="One of the accounts is closed")
        else:
            get_account_from = get_account_bank_extern(body.iban_from, session)
            if get_account_to.is_closed:
                raise HTTPException(status_code=400, detail="One of the accounts is closed")
            if get_account_from.balance < body.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            if not get_account_from or not get_account_to:
                raise HTTPException(status_code=404, detail="One of the accounts not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if body.action != ActionEnum.deposite:
        body.iban_bank_from = "None"

    if body.name == "" or body.name == "string":
        body.name = f"{body.action.name} de {body.amount} robux"

    transaction = Transaction(
        iban_from=body.iban_from,
        iban_to=body.iban_to,
        iban_bank_from=body.iban_bank_from,
        amount=body.amount,
        action=body.action,
        name=body.name,
        status="pending"
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return {"message": "Transaction initiated, pending finalization.", "transaction_id": transaction.id,
            "iban_bank_from": transaction.iban_bank_from}


###########################
#     Get Transaction Info
###########################
def get_transaction(id: int, get_user: get_user, session: Session):
    """ Get information about a specific transaction """
    transaction = session.query(Transaction).filter(Transaction.id == id).first()
    if not transaction or transaction == None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


######################
#     Get All Transaction Info
####################
def get_all_transaction(iban: str, query_params_group_by: str, get_user: get_user, session=Depends(get_session)):
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
            "iban_bank_from": transaction.iban_bank_from,
            "account_name": account_name,
            "amount": transaction.amount,
            "action": transaction.action,
            "status": transaction.status,
            "transaction_name": transaction.name,
            "timestamp": transaction.timestamp
        })

    if query_params_group_by == "date":
        array = [{day: list(groupe) for day, groupe in groupby(array, key=lambda t: t["timestamp"].date())}]

    return array


######################
#     Get Iban Of User Account
####################
def get_iban_from(id: int, get_user: get_user, session=Depends(get_session)):
    """ Get the IBAN of the user's account """
    transaction = get_transaction(id, get_user, session)
    if transaction:
        return transaction.iban_from


######################
#     Get Iban Of Beneficiary Account
####################
def get_iban_to(id: int, session=Depends(get_session)):
    """ Get the IBAN of the beneficiary's account """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.iban_to


######################
#     Get transaction amount
####################
def get_amount(id: int, session=Depends(get_session)):
    """ Get the amount of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.amount


######################
#     Get transaction action
####################
def get_action(id: int, session=Depends(get_session)):
    """ Get the action of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.action


######################
#     Get Transaction date
####################
def get_date(id: int, session=Depends(get_session)):
    """ Get the date of the transaction """
    transaction = get_transaction(id, session)
    if transaction:
        return transaction.timestamp


######################
#     Cancel Transaction
####################
def cancel_transaction(id: int, user: get_user, session: Session):
    transaction = get_transaction(id, user, session)
    iban_from = transaction.iban_from

    current_user = get_all_information(user, session)
    uid_current_user = current_user["uid"]

    uid_user_bank_account = get_uid(iban_from, session)

    print(uid_current_user)
    print(uid_user_bank_account)

    if transaction.status == "completed":
        raise HTTPException(status_code=400, detail="Transaction already completed")

    if transaction.status == "cancel":
        raise HTTPException(status_code=400, detail="Transaction already canceled")

    if uid_current_user != uid_user_bank_account:
        raise HTTPException(status_code=403, detail="Forbidden")

    if iban_from == transaction.iban_from:
        if transaction.status == "pending":
            transaction.status = "cancel"
            session.commit()
            session.refresh(transaction)


    else:
        raise HTTPException(status_code=400, detail="Invalid IBAN")
    return transaction
