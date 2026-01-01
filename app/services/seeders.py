
from fastapi import Depends
from sqlmodel import Session
from app.models.models_create import Init_User
from app.services import init_user
from app.settings.schemas import Bank_Extern
from app.settings.database import get_session
from app.settings.config import BANK_NAME



def bank_extern_create(session : Session):
    """ Seed the database with initial external banks if they don't exist """
    bank_exist = session.query(Bank_Extern).all()
    if not bank_exist:
        bank_main = Bank_Extern(
            is_main=True,
            name="Banque de France",
            iban="FR76000000000000000000000CENTRAL",
            balance=99999999.0
        )
        mega_bank = Bank_Extern(
            is_main=False,
            name="TechCorp Payroll",
            iban="FR7699998888777766665555CORP01",
            balance=500000.0

            )
        session.add(bank_main)
        session.add(mega_bank)
        session.commit()
        session.refresh(bank_main)
        session.refresh(mega_bank)