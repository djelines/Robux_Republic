import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.models.models import ActionEnum
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account, Bank_Extern

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def process_pending_transactions():
    """Logic to finalize pending transactions moved to async for Render compatibility"""
    print(f"🔎 {datetime.now().strftime('%H:%M:%S')} - Scanning for pending transactions...")
    db_session = SessionLocal()
    
    try:
        # On définit le délai de 5 secondes
        time_off = datetime.now() - timedelta(seconds=5)

        # Récupération des transactions 'pending'
        pending_transactions = db_session.query(Transaction).filter(
            Transaction.status == "pending",
            Transaction.timestamp <= time_off  
        ).all()

        if not pending_transactions:
            return

        for transaction in pending_transactions:
            error_deposite = False
            error = False
            account_from = None
            
            # 1. Identifier le compte destinataire (interne)
            account_to = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
            
            if not account_to:
                transaction.status = "error"
                continue

            # 2. Identifier le compte émetteur selon l'action
            if transaction.action == ActionEnum.virement:
                account_from = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
           
            elif transaction.action == ActionEnum.deposite:
                account_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_from).first()
                
                # Logique spécifique Bank_Extern
                if transaction.iban_bank_from is not None:
                    account_bank_from = db_session.query(Bank_Extern).filter(Bank_Extern.iban == transaction.iban_bank_from).first()
                    if account_bank_from and account_bank_from.balance < transaction.amount:
                        error_deposite = True
                    
                    if not error_deposite and account_bank_from:
                        account_bank_from.balance -= transaction.amount
                        account_from.balance += transaction.amount

            # 3. Vérifications des soldes et statut du compte
            if not error_deposite and account_from:
                if account_from.balance < transaction.amount:
                    error = True
                if account_to.is_closed:
                    error = True

                # 4. Exécution du transfert
                if not error:
                    account_from.balance -= transaction.amount
                    account_to.balance += transaction.amount
                    transaction.status = "completed"
                    print(f"✅ Transaction {transaction.id} SUCCESS")
                else:
                    transaction.status = "error"
                    print(f"❌ Transaction {transaction.id} ERROR (insufficient funds or closed account)")
            else:
                transaction.status = "error"

        db_session.commit()

    except Exception as e:
        db_session.rollback()
        print(f"⚠️ Global Error in scheduler: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    # Utilisation de l'Event Loop AsyncIO (Comme ton script Mail)
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(event_loop=loop)
    
    # On lance la tâche toutes les 5 secondes
    scheduler.add_job(process_pending_transactions, 'interval', seconds=5)

    print("🚀 SCHEDULER FINALIZE (ASYNC MODE) - Started")
    try:
        # On exécute une première fois au démarrage
        loop.create_task(process_pending_transactions())
        scheduler.start()
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()