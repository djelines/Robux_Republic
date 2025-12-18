# python -m app.schelduler.finalize_transaction
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.models.models import ActionEnum
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account ,Bank_Extern

from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi import HTTPException

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""This module handles the periodic finalization of pending transactions"""


def get_account(session, iban, is_external=False):
    """Fetch a bank account or external account by IBAN"""
    model = Bank_Extern if is_external else Bank_Account
    return session.query(model).filter(model.iban == iban).first()


def process_transaction(session, transaction):
    """Process a single transaction, return True if successful, False otherwise"""
    error_deposit = False
    error = False

    # Determine source account
    if transaction.action == ActionEnum.virement:
        account_from = get_account(session, transaction.iban_from)
    elif transaction.action == ActionEnum.deposite:
        account_from = get_account(session, transaction.iban_from, is_external=True)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {transaction.action}")

    # Determine destination account
    account_to = get_account(session, transaction.iban_to)

    # Optional bank account involvement
    account_bank_from = None
    if transaction.iban_bank_from:
        account_bank_from = get_account(session, transaction.iban_bank_from, is_external=True)
        if account_bank_from.balance < transaction.amount:
            error_deposit = True
        else:
            account_bank_from.balance -= transaction.amount
            account_from.balance += transaction.amount

    # Check basic errors
    if not error_deposit:
        if account_from.balance < transaction.amount or account_to.is_closed:
            error = True

    # Apply transaction
    if not error:
        account_from.balance -= transaction.amount
        account_to.balance += transaction.amount
        transaction.status = "completed"
    else:
        transaction.status = "error"


def process_pending_transactions():
    db_session = SessionLocal()
    try:
        time_off = datetime.now() - timedelta(seconds=5)
        pending_transactions = (
            db_session.query(Transaction)
            .filter(Transaction.status == "pending", Transaction.timestamp <= time_off)
            .with_for_update()
            .all()
        )

        for tx in pending_transactions:
            process_transaction(db_session, tx)

        db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Transaction processing error: " + str(e))

    finally:
        db_session.close()



if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(process_pending_transactions, 'interval', seconds=5)

    try:
        process_pending_transactions() 
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        raise 