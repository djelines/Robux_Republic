import asyncio
import time
from datetime import datetime, timedelta
from app.services.mail import EmailSchema, simple_send
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.models import ActionEnum 
from app.services.user_bank_account import get_all_accounts
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account ,Bank_Extern, User_Bank_Account,Auth
from app.settings.config import CEILING_ACCOUNT

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def process_email_send():
    with SessionLocal() as db_session:
        try:
            all_transactions = (
                db_session.query(Transaction)
                .filter(Transaction.status == "completed", Transaction.is_mail_send == False)
                .with_for_update() 
                .all()
            )
            
            if not all_transactions:
                return

            for transaction in all_transactions:
                
                
                bank_id_from = db_session.query(Bank_Account.id).filter(
                    Bank_Account.iban == transaction.iban_from).scalar()
                uid_user_from = db_session.query(User_Bank_Account.uid).filter(
                    User_Bank_Account.bank_account_id == bank_id_from).scalar()
                email_user_from = db_session.query(Auth.email).filter(
                    Auth.uid == uid_user_from).scalar()


                bank_id_to = db_session.query(Bank_Account.id).filter(
                    Bank_Account.iban == transaction.iban_to).scalar()
                uid_user_to = db_session.query(User_Bank_Account.uid).filter(
                    User_Bank_Account.bank_account_id == bank_id_to).scalar()
                email_user_to = db_session.query(Auth.email).filter(
                    Auth.uid == uid_user_to).scalar()

                message_from = f"Votre transaction de {transaction.amount} à {transaction.iban_to} a été effectuée avec succès."
                message_to = f"Vous avez reçu une transaction de {transaction.amount} d'un montant de : {transaction.iban_from}."
                
                
                if email_user_from:
                    response_from = await simple_send(EmailSchema(email=[email_user_from]), message_from)
                    if response_from and response_from.status_code == 200:
                        transaction.is_mail_send = True
                
                if email_user_to:
                    response_to = await simple_send(EmailSchema(email=[email_user_to]), message_to)
                    if response_to and response_to.status_code == 200:
                        transaction.is_mail_send = True 

            db_session.commit()
            
        except Exception as e:
            db_session.rollback()

if __name__ == "__main__":
    executors = {
        'default': {'type': 'threadpool'},
        'asyncio': {'type': 'asyncio'}
    }
    
    loop = asyncio.get_event_loop()
    
    scheduler = AsyncIOScheduler(executors=executors, event_loop=loop)
    
    scheduler.add_job(process_email_send, 'interval', seconds=4, executor='asyncio')

    try:
        scheduler.start()
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    except Exception as e:
        scheduler.shutdown()
