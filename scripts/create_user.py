#!/usr/bin/env python3
"""
CLI script to create a user account.
Usage: python -m scripts.create_user
       (or: python scripts/create_user.py)

Never use the public /auth/signup endpoint in production.
"""
import getpass
import sys
import uuid

# Ensure the project root is on sys.path when run as a script
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.settings.database import get_session, create_db_and_tables
from app.settings.schemas import Auth, User
from app.services.bank_account import create_bank_account as _create_bank_account
from app.utils.utils import hash_password


def create_user_cli():
    print("=== Création d'un compte utilisateur ===")
    print()

    # Collect input
    first_name = input("Prénom : ").strip()
    if not first_name:
        print("Erreur : le prénom est requis.", file=sys.stderr)
        sys.exit(1)

    last_name = input("Nom : ").strip()
    if not last_name:
        print("Erreur : le nom est requis.", file=sys.stderr)
        sys.exit(1)

    address = input("Adresse : ").strip()

    email = input("Email : ").strip().lower()
    if not email or "@" not in email:
        print("Erreur : email invalide.", file=sys.stderr)
        sys.exit(1)

    password = getpass.getpass("Mot de passe : ")
    if len(password) < 8:
        print("Erreur : le mot de passe doit contenir au moins 8 caractères.", file=sys.stderr)
        sys.exit(1)

    password_confirm = getpass.getpass("Confirmer le mot de passe : ")
    if password != password_confirm:
        print("Erreur : les mots de passe ne correspondent pas.", file=sys.stderr)
        sys.exit(1)

    # Init DB
    create_db_and_tables()
    session = next(get_session())

    try:
        # Check email uniqueness
        existing = session.query(Auth).filter(Auth.email == email).first()
        if existing:
            print(f"Erreur : l'email {email} est déjà utilisé.", file=sys.stderr)
            sys.exit(1)

        uid = str(uuid.uuid4())

        new_user = User(
            uid=uid,
            first_name=first_name,
            last_name=last_name,
            address=address,
        )
        session.add(new_user)
        session.flush()

        new_auth = Auth(
            uid=uid,
            email=email,
            password=hash_password(password),
        )
        session.add(new_auth)
        session.commit()

        print()
        print(f"✅ Utilisateur créé avec succès.")
        print(f"   UID   : {uid}")
        print(f"   Email : {email}")
        print(f"   Nom   : {first_name} {last_name}")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de la création : {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    create_user_cli()
