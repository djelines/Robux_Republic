

from fastapi import Depends
from app.models.models_create import Init_User
from app.services.auth import create_auth
from app.services.bank_account import create_bank_account
from app.services.bank_account import create_bank_account
from app.settings.database import get_session
from app.utils.utils import generate_uid
from app.services.user import get_all as get_user_info


def init_user(body: Init_User, session=Depends(get_session)):
    """ Initialize a new user with default settings """
    
    body.auth.uid = generate_uid()  # Ensure the user has a unique identifier
    body.bank_account.uid = body.auth.uid  # Link bank account to the user
    create_auth(body.auth, session)
    
    body.bank_account.is_principal = True
    body.bank_account.is_closed = False
    body.bank_account.balance = 10000000000.0
    body.bank_account.bank_account_id = None
    body.bank_account.iban = None
    body.bank_account.name = "Compte Principal"
    
    bank_account = create_bank_account(body.bank_account, True ,session)
    
    user = get_user_info(body.auth.uid, session)
    
    return {
        "user":  user,
        "bank_account": bank_account
    }
    
