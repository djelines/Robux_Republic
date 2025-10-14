from app.settings.schemas import Bank_Account
from app.settings.database import get_session
from fastapi import Depends


def create_bank_account():
    """ Create a new bank account """
    pass

def get_all():
    """ Get all information about bank accounts """
    pass

def get_account(iban: str , session=Depends(get_session)) -> Bank_Account:
    return session.query(Bank_Account).filter(Bank_Account.iban == iban).first()

def get_is_principal():
    """ Check if the bank account is a principal account """
    pass

def get_is_closed():
    """ Check if the bank account is closed """
    pass

def get_iban():
    """ Get the IBAN of the bank account """
    pass

def get_balance():
    """ Get the solde of the bank account """
    pass

def update_is_closed():
    """ Update the closed status of the bank account and related user bank accounts """
    pass

def update_balance():
    """ Update the balance of the bank account """
    pass