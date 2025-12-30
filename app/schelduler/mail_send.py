import asyncio
from app.services.mail import EmailSchema, simple_send
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.settings.database import engine
from app.settings.schemas import Transaction, Bank_Account, User_Bank_Account, Auth
from sqlalchemy import update

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_pro_template(title, message, amount, iban_source, iban_dest):
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f6f9fc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f6f9fc; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 500px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                        <tr>
                            <td style="padding: 30px 40px; text-align: left; border-bottom: 1px solid #f0f0f0;">
                                <div style="font-size: 20px; font-weight: 700; color: #1a1f36; letter-spacing: -0.5px;">Banque Republic</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="margin: 0 0 16px; font-size: 22px; color: #1a1f36; font-weight: 600;">{title}</h2>
                                <p style="margin: 0 0 24px; font-size: 16px; line-height: 1.6; color: #4f566b;">{message}</p>
                                
                                <div style="background-color: #f8fafd; border-radius: 8px; padding: 24px; border: 1px solid #e3e8ee;">
                                    <div style="font-size: 13px; color: #697386; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Montant</div>
                                    <div style="font-size: 28px; font-weight: 700; color: #2ecc71; margin-bottom: 24px;">{amount} R$</div>
                                    
                                    <div style="margin-bottom: 16px;">
                                        <div style="font-size: 12px; color: #697386; margin-bottom: 4px;">Source</div>
                                        <div style="font-size: 13px; color: #1a1f36; font-family: monospace; word-break: break-all; background: #fff; padding: 8px; border-radius: 4px; border: 1px solid #e3e8ee;">{iban_source}</div>
                                    </div>
                                    
                                    <div>
                                        <div style="font-size: 12px; color: #697386; margin-bottom: 4px;">Destinataire</div>
                                        <div style="font-size: 13px; color: #1a1f36; font-family: monospace; word-break: break-all; background: #fff; padding: 8px; border-radius: 4px; border: 1px solid #e3e8ee;">{iban_dest}</div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 0 40px 40px; text-align: center;">
                                <p style="font-size: 13px; color: #697386; margin: 0 0 16px;">Ceci est une notification automatique. Merci de ne pas répondre.</p>
                                <div style="height: 1px; background-color: #e3e8ee; margin-bottom: 20px;"></div>
                                <div style="font-size: 12px; color: #a3acb9;">&copy; 2025 banque-republic.micdev.fr | Banque Republic System</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

async def process_email_send():
    with SessionLocal() as db_session:
        try:
            all_transactions = (
                db_session.query(Transaction)
                .filter(Transaction.status == "completed", Transaction.is_mail_send == False)
                .with_for_update(skip_locked=True) 
                .all()
            )
            
            if not all_transactions: return

            for transaction in all_transactions:
                email_from = None
                bank_f = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_from).first()
                if bank_f:
                    u_bank = db_session.query(User_Bank_Account).filter(User_Bank_Account.bank_account_id == bank_f.id).first()
                    if u_bank:
                        email_from = db_session.query(Auth.email).filter(Auth.uid == u_bank.uid).scalar()

                email_to = None
                bank_t = db_session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first()
                if bank_t:
                    u_bank = db_session.query(User_Bank_Account).filter(User_Bank_Account.bank_account_id == bank_t.id).first()
                    if u_bank:
                        email_to = db_session.query(Auth.email).filter(Auth.uid == u_bank.uid).scalar()

                mail_sent = False
                
                if email_from:
                    html = get_pro_template("Transaction envoyée", "Votre transfert a été validé.", transaction.amount, transaction.iban_from, transaction.iban_to)
                    if await simple_send(EmailSchema(email=[email_from]), html): 
                        mail_sent = True
                
                if email_to:
                    html = get_pro_template("Crédit reçu", "Votre compte a été crédité.", transaction.amount, transaction.iban_from, transaction.iban_to)
                    if await simple_send(EmailSchema(email=[email_to]), html): 
                        mail_sent = True

                if mail_sent or (not email_from and not email_to):
                    transaction.is_mail_send = True
                    db_session.commit()
                    db_session.begin() 
            
        except Exception as e:
            db_session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(process_email_send, 'interval', seconds=5)
    try:
        scheduler.start()
        loop.run_forever()
    except: pass