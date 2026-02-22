"""
CLI script to create a user with a principal bank account.
Usage (from backend/Robux_Republic/):
    python -m scripts.create_user
"""
import getpass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.settings.database import get_session, create_db_and_tables
from app.services.seeders import bank_extern_create
from app.models.models_create import Auth_create, Bank_Account_create, Init_User
from app.services.init_user import init_user
from app.settings.schemas import Auth


def main():
    print("=== Création d'un nouvel utilisateur ===\n")

    first_name = input("Prénom       : ").strip()
    last_name   = input("Nom          : ").strip()
    address     = input("Adresse      : ").strip()
    email       = input("Email        : ").strip().lower()
    password    = getpass.getpass("Mot de passe : ")
    confirm     = getpass.getpass("Confirmer    : ")

    if not all([first_name, last_name, email, password]):
        print("\n[ERREUR] Tous les champs obligatoires doivent être remplis.")
        sys.exit(1)

    if "@" not in email:
        print("\n[ERREUR] Email invalide.")
        sys.exit(1)

    if len(password) < 8:
        print("\n[ERREUR] Le mot de passe doit contenir au moins 8 caractères.")
        sys.exit(1)

    if password != confirm:
        print("\n[ERREUR] Les mots de passe ne correspondent pas.")
        sys.exit(1)

    create_db_and_tables()
    session = next(get_session())

    try:
        existing = session.query(Auth).filter(Auth.email == email).first()
        if existing:
            print(f"\n[ERREUR] L'email {email} est déjà utilisé.")
            sys.exit(1)

        bank_extern_create(session)

        body = Init_User(
            auth=Auth_create(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                address=address,
            ),
            bank_account=Bank_Account_create(),
        )

        result = init_user(body, session)
        user    = result["user"]
        account = result["bank_account"]

        print(f"\n[OK] Utilisateur créé :")
        print(f"     UID   : {user.uid}")
        print(f"     Email : {email}")
        print(f"     IBAN  : {account.iban}")
        print(f"     Solde : {account.balance} €")

    except Exception as e:
        session.rollback()
        print(f"\n[ERREUR] {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
