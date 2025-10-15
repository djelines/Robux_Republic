from fastapi import Depends , FastAPI
from sqlmodel import Session
from app.settings.schemas import Bank_Account, User_Bank_Account , User
from app.settings.database import create_db_and_tables, get_session, engine
from routes.transactions import router as transactions_router
from routes.beneficiaires import router as beneficiaires_router
from routes.auth import router as authentification_router
from routes.bank_account import router as bank_account_router


app = FastAPI()
app.include_router(transactions_router)
app.include_router(bank_account_router)
app.include_router(beneficiaires_router)

app.include_router(authentification_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI fonctionne !"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
    
    # user1= User(uid="123",first_name="Clement", last_name="Dupont", address="123 Rue Principale")
    # user2= User(uid="456",first_name="Marie", last_name="Curie", address="456 Avenue des Sciences")
    
    
    # bank_account1= Bank_Account(is_principal=True, is_closed=False, iban="FR7612345678901234567890123", balance=1000.0)
    # bank_account2= Bank_Account(is_principal=False, is_closed=False, iban="FR7612345678901234567890456", balance=500.0)
    
    # user_bank_account1= User_Bank_Account(uid=user1.uid, bank_account_id=1, name="Compte Courant")
    # user_bank_account2= User_Bank_Account(uid=user2.uid, bank_account_id=2, name="Compte Epargne")

    # with Session(engine) as session:
    #     session.add(user1)
    #     session.add(user2)
    #     session.add(bank_account1)
    #     session.add(bank_account2)
    #     session.add(user_bank_account1)
    #     session.add(user_bank_account2)
    #     session.commit()
    # return {"message": "Database and tables created, sample data inserted."}
    