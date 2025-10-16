from fastapi import Depends , FastAPI
from sqlmodel import Session
from app.services.seeders import bank_extern_create
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
    session = next(get_session())
    create_db_and_tables()
    bank_extern_create(session)
    
    

    # with Session(engine) as session:
    #     session.add(user1)
    #     session.add(user2)
    #     session.add(bank_account1)
    #     session.add(bank_account2)
    #     session.add(user_bank_account1)
    #     session.add(user_bank_account2)
    #     session.commit()
    # return {"message": "Database and tables created, sample data inserted."}
    