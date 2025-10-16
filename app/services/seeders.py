
from fastapi import Depends
from sqlmodel import Session
from app.models.models_create import Init_User
from app.services import init_user
from app.settings.schemas import Bank_Extern
from app.settings.database import get_session



def bank_extern_create(session : Session):
    """ Seed the database with initial external banks if they don't exist """
    bank_exist = session.query(Bank_Extern).all()
    if not bank_exist:
        bank_main = Bank_Extern(
            is_main=True,
            name="Robux",
            iban="FR7612345678901234567890123RobuxBankTowerTrump",
            balance=999999999999.0
        )
        mega_bank = Bank_Extern(
            is_main=False,
            name="Mega Bank",
            iban="FR7612345678901234567890123MegaBankTowerGretaThunberg",
            balance=100000000.0

            ) 
        session.add(bank_main)
        session.add(mega_bank)
        session.commit()
        session.refresh(bank_main)
        session.refresh(mega_bank)