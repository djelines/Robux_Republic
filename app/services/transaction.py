
from app.settings.schemas import Bank_Account, Transaction, User_Bank_Account
from app.services.bank_account import get_account
from app.settings.database import get_session
from fastapi import Depends

def create_transaction(body: Transaction, session=Depends(get_session)):
    """ Create a new transaction """
    get_account_from = get_account(body.iban_from , session)
    get_account_to = get_account(body.iban_to , session)

    if(body.iban_from == body.iban_to):
        return {"error": "Cannot transfer to the same account"}
    if(body.amount <= 0):
        return {"error": "Invalid transaction amount"}
    if (get_account_from.balance < body.amount):
        return {"error": "Insufficient funds"}
    if (get_account_from.is_closed):
        return {"error": "Sender's account is closed"}
    if (get_account_to.is_closed):
        return {"error": "Recipient's account is closed"}
    
    get_account_from.balance -= body.amount
    get_account_to.balance += body.amount
    
    transaction = Transaction(
        iban_from=body.iban_from,
        iban_to=body.iban_to,
        amount=body.amount,
        action=body.action
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def get_transaction():
    """ Get information about a specific transaction """
    pass

def get_all_transaction(iban: str ,session=Depends(get_session)):
    """ Get all information about transactions """
    
    array = []
    transactions = session.query(Transaction).filter(
        (Transaction.iban_from == iban)).order_by(Transaction.timestamp.desc()).all()

    for transaction in transactions:
        id = session.query(Bank_Account).filter(Bank_Account.iban == transaction.iban_to).first().id
        account_name= session.query(User_Bank_Account).filter(User_Bank_Account.bank_account_id== id).first().name
        array.append({
            "id": transaction.id,
            "iban_from": transaction.iban_from,
            "iban_to": transaction.iban_to,
            "account_name": account_name,
            "amount": transaction.amount,
            "action": transaction.action,
            "timestamp": transaction.timestamp
        })

    return array

def get_iban_from():
    """ Get the IBAN of the user's account """
    pass

def get_iban_to():
    """ Get the IBAN of the beneficiary's account """
    pass

def get_amount():
    """ Get the amount of the transaction """
    pass

def get_action():
    """ Get the action of the transaction """
    pass

def get_date():
    """ Get the date of the transaction """
    pass

def delete_transaction():
    """ Delete a specific transaction """
    pass