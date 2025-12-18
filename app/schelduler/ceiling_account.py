# python -m app.schelduler.process_ceiling_account
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.models.models import ActionEnum
from app.services.user_bank_account import get_all_accounts
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account ,Bank_Extern, User_Bank_Account
from app.settings.config import CEILING_ACCOUNT

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_ceiling_accounts():
    """Process bank accounts that exceed the ceiling limit and transfer excess to principal account."""
    with SessionLocal() as db_session:
        try:
             # Retrieve all non-principal accounts exceeding the ceiling
            all_accounts = (
                db_session.query(Bank_Account)
                .filter(Bank_Account.balance > CEILING_ACCOUNT, Bank_Account.is_principal == False)
                .with_for_update() 
                .all()
            )
            
            if not all_accounts:
                return

            for account in all_accounts:
                amount_difference = account.balance - CEILING_ACCOUNT
                # Get user link to account
                user_bank_link = db_session.query(User_Bank_Account).filter(
                    User_Bank_Account.bank_account_id == account.id
                ).first()
                
                all_transactions = db_session.query(Transaction).filter(
                    Transaction.iban_from == account.iban,
                    Transaction.status == "pending",
                    Transaction.if_started == True
                ).all()

                if all_transactions:
                   continue

                if not user_bank_link:
                    continue
                
                # Get user id for get all accounts of user
                uid_user = user_bank_link.uid
                all_accounts_user = get_all_accounts(uid_user, "", None, db_session)

                principal_account_id = None
                for account_info in all_accounts_user:
                    # for each account of user, check if is principal and get id
                    if account_info.is_principal:
                        principal_account_id = account_info.id
                        break
                
                if not principal_account_id:
                    continue
                #Get principal account info 
                principal_account = db_session.query(Bank_Account).filter(
                    Bank_Account.id == principal_account_id
                ).with_for_update().first()

                if not principal_account:
                    continue
                # Initiate a transaction to transfer the excess amount to the principal account 
                virement_transaction = Transaction(
                    iban_from=account.iban,
                    iban_to=principal_account.iban,
                    iban_bank_from="None",
                    amount=amount_difference,
                    action=ActionEnum.virement,
                    name=f"Virement automatique du compte {account.iban} vers le compte principal {principal_account.iban} car plafond dépassé",
                    status="pending",
                    timestamp=datetime.now(),
                    if_started=True
                )
                db_session.add(virement_transaction)

                # If you want to immediately update balances (optional, as transaction finalization will handle it)
                # principal_account.balance += amount_difference
                # account.balance -= amount_difference

            db_session.commit()

        except Exception as e:
            db_session.rollback()
            raise 

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(process_ceiling_accounts, 'interval', seconds=4)

    try:
        process_ceiling_accounts() 
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass