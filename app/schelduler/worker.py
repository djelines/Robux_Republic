import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Imports originaux
from app.services.mail import EmailSchema, simple_send
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account, Bank_Extern, User_Bank_Account, Auth
from app.models.models import ActionEnum

# Configuration des logs pour Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- FONCTION 1 : MAIL SEND (Issue de votre script 1) ---
async def process_email_send():
    logger.info("📧 Vérification des emails...")
    with SessionLocal() as db_session:
        try:
            all_transactions = (
                db_session.query(Transaction)
                .filter(Transaction.status == "completed", Transaction.is_mail_send == False)
                .all()
            )
            
            for transaction in all_transactions:
                # Logique IBAN FROM
                bank_id_from = db_session.query(Bank_Account.id).filter(Bank_Account.iban == transaction.iban_from).scalar()
                uid_user_from = db_session.query(User_Bank_Account.uid).filter(User_Bank_Account.bank_account_id == bank_id_from).scalar()
                email_user_from = db_session.query(Auth.email).filter(Auth.uid == uid_user_from).scalar()

                # Logique IBAN TO
                bank_id_to = db_session.query(Bank_Account.id).filter(Bank_Account.iban == transaction.iban_to).scalar()
                uid_user_to = db_session.query(User_Bank_Account.uid).filter(User_Bank_Account.bank_account_id == bank_id_to).scalar()
                email_user_to = db_session.query(Auth.email).filter(Auth.uid == uid_user_to).scalar()

                if email_user_from:
                    msg = f"Votre transaction de {transaction.amount} à {transaction.iban_to} a été effectuée."
                    resp = await simple_send(EmailSchema(email=[email_user_from]), msg)
                    if resp and resp.status_code == 200:
                        transaction.is_mail_send = True
                
                if email_user_to:
                    msg = f"Vous avez reçu {transaction.amount} de {transaction.iban_from}."
                    resp = await simple_send(EmailSchema(email=[email_user_to]), msg)
                    if resp and resp.status_code == 200:
                        transaction.is_mail_send = True 

            db_session.commit()
        except Exception as e:
            logger.error(f"Erreur Mail: {e}")
            db_session.rollback()

# --- FONCTION 2 : PENDING TRANSAC (Issue de votre script 2) ---
async def process_pending_transactions():
    logger.info(f"🔎 Scan des transactions en attente...")
    with SessionLocal() as db_session:
        try:
            time_off = datetime.now() - timedelta(seconds=5)
            pending_transactions = db_session.query(Transaction).filter(
                Transaction.status == "pending",
                Transaction.timestamp <= time_off  
            ).all()

            for transaction in pending_transactions:
                error_deposite = False
                error = False
                account_to = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
                
                if not account_to:
                    transaction.status = "error"
                    continue

                if transaction.action == ActionEnum.virement:
                    account_from = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
                elif transaction.action == ActionEnum.deposite:
                    account_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_from).first()
                    if transaction.iban_bank_from:
                        acc_bank_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_bank_from).first()
                        if acc_bank_from and acc_bank_from.balance < transaction.amount:
                            error_deposite = True
                        elif acc_bank_from:
                            acc_bank_from.balance -= transaction.amount
                            account_from.balance += transaction.amount

                if not error_deposite and account_from:
                    if account_from.balance < transaction.amount or account_to.is_closed:
                        error = True
                    if not error:
                        account_from.balance -= transaction.amount
                        account_to.balance += transaction.amount
                        transaction.status = "completed"
                        logger.info(f"✅ Succès {transaction.id}")
                    else:
                        transaction.status = "error"
                else:
                    transaction.status = "error"
            db_session.commit()
        except Exception as e:
            logger.error(f"Erreur Transac: {e}")
            db_session.rollback()

# --- SCHEDULER UNIQUE ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(event_loop=loop)

    # On garde vos délais mais on les espace un peu pour Render Free
    scheduler.add_job(process_pending_transactions, 'interval', seconds=15)
    scheduler.add_job(process_email_send, 'interval', seconds=30)

    try:
        scheduler.start()
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()