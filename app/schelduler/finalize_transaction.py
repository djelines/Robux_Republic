# python -m app.schelduler.finalize_transaction
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

""" This module handles the periodic finalization of pending transactions"""
def process_pending_transactions():
    db_session = SessionLocal()
    
    try:
        time_off = datetime.now() - timedelta(seconds=5)

        pending_transactions = db_session.query(Transaction).filter(
            Transaction.status == "pending",
            Transaction.timestamp <= time_off  
        ).with_for_update().all()

        if not pending_transactions:
            raise HTTPException(status_code=400, detail="No pending transactions to process")
             
        for transaction in pending_transactions:
            
            account_from = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
            account_to = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
            
            if account_from == account_to:
                raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
            if transaction.amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid transaction amount")
            if account_from.balance < transaction.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            if not account_from or not account_to:
                raise HTTPException(status_code=404, detail="One of the accounts not found")
            if account_from.is_closed or account_to.is_closed:
                raise HTTPException(status_code=400, detail="One of the accounts is closed")
            
            account_from.balance -= transaction.amount
            account_to.balance += transaction.amount
            transaction.status = "completed"
    
        db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail="Transaction processing error / " + str(e))
    finally:
        db_session.close()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(process_pending_transactions, 'interval', seconds=5)

    try:
        process_pending_transactions() 
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass