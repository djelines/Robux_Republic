from fastapi import Depends , FastAPI
from sqlmodel import Session

from app.services import transaction
from app.services.seeders import bank_extern_create
from app.settings.schemas import Bank_Account, User_Bank_Account, User, Transaction, Bank_Extern
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
    delete_transaction()
    bank_extern_create(session)




def delete_transaction():
    session = next(get_session())
    try:
        # 1. Ciblez la table Transaction et appelez la méthode de suppression en masse
        nombre_de_lignes_supprimees = session.query(Transaction).delete()

        # 2. Validez la transaction pour rendre la suppression permanente
        session.commit()

        print(f"Succès ! {nombre_de_lignes_supprimees} lignes ont été supprimées de la table Transaction.")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        # En cas d'erreur, annulez toutes les modifications
        session.rollback()
    finally:
        # Fermez la session pour libérer la connexion
        session.close()
    # with Session(engine) as session:
    #     session.add(user1)
    #     session.add(user2)
    #     session.add(bank_account1)
    #     session.add(bank_account2)
    #     session.add(user_bank_account1)
    #     session.add(user_bank_account2)
    #     session.commit()
    # return {"message": "Database and tables created, sample data inserted."}
    