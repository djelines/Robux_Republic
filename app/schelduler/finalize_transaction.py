# python -m app.schelduler.finalize_transaction
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.models.models import ActionEnum
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account ,Bank_Extern

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_pending_transactions():
    """ This module handles the periodic finalization of pending transactions"""
    error_deposite=False
    global account_from
    db_session = SessionLocal()
    error=False
    
    try:
        time_off = datetime.now() - timedelta(seconds=5)

        pending_transactions = db_session.query(Transaction).filter(
            Transaction.status == "pending",
            Transaction.timestamp <= time_off  
        ).with_for_update().all()


        for transaction in pending_transactions:
            account_to = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
            
            if transaction.action == ActionEnum.virement :
                account_from = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
           
            elif transaction.action == ActionEnum.deposite :
                account_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_from).first()
                
                if transaction.iban_bank_from is not None:
                    account_bank_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_bank_from).first()
                    if account_bank_from.balance < transaction.amount:
                        error_deposite=True
                    if not error_deposite:
                        account_bank_from.balance -= transaction.amount
                        account_from.balance += transaction.amount
            if not error_deposite:
                if account_from.balance < transaction.amount:
                    error=True
                if account_to.is_closed:
                    error=True

                if not error:
                    account_from.balance -= transaction.amount
                    account_to.balance += transaction.amount
                    transaction.status = "completed"
                else:
                    transaction.status = "error"

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