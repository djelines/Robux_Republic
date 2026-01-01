import pytest
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.settings.schemas import Bank_Account, User, Bank_Extern, User_Bank_Account
from app.models.models import get_db_engine
from app.models.models_create import Bank_Account_create
from app.settings.database import SQLModel
from app.services.bank_account import create_bank_account
from app.services.user_bank_account import get_bank_id
from fastapi import HTTPException


@pytest.fixture()
def test_db_session():
    """Create an in-memory SQLite database for testing"""
    engine = get_db_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    SQLModel.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def test_user(test_db_session):
    """Create a test user"""
    user = User(
        uid="test-uid-123",
        first_name="John",
        last_name="Doe",
        address="123 Test Street"
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture()
def test_bank_extern(test_db_session):
    """Create a test external bank (main bank)"""
    bank = Bank_Extern(
        is_main=True,
        name="Robux",
        iban="FR7612345678901234567890123TestBank",
        balance=Decimal("999999999999.0")
    )
    test_db_session.add(bank)
    test_db_session.commit()
    test_db_session.refresh(bank)
    return bank


@pytest.fixture()
def mock_get_user():
    """Mock the get_user dependency"""
    class MockUser:
        uid = "test-uid-123"
    return MockUser()


def test_create_bank_account_success(test_db_session, test_user, test_bank_extern, mock_get_user):
    """Test successful bank account creation"""

    account_data = Bank_Account_create(
        uid=test_user.uid,
        name="Mon Compte Principal",
        is_principal=True
    )

    result = create_bank_account(account_data, mock_get_user, test_db_session)

    assert result is not None
    assert "bank_account" in result
    assert "user_bank_account" in result

    bank_account = result["bank_account"]
    user_bank_account = result["user_bank_account"]

    # Verify bank account properties
    assert bank_account.iban is not None
    assert len(bank_account.iban) > 0
    assert bank_account.is_principal is True
    assert bank_account.is_closed is False
    assert bank_account.balance == Decimal("0")

    # Verify user bank account properties
    assert user_bank_account.uid == test_user.uid
    assert user_bank_account.name == "Mon Compte Principal"
    assert user_bank_account.bank_account_id == bank_account.id
    assert user_bank_account.bank_id == test_bank_extern.id


def test_create_bank_account_missing_uid(test_db_session, test_bank_extern, mock_get_user):
    """Test that creating account without uid returns error"""

    account_data = Bank_Account_create(
        uid=None,
        name="Mon Compte"
    )

    result = create_bank_account(account_data, mock_get_user, test_db_session)

    assert "error" in result
    assert "Valeurs manquantes" in result["error"]


def test_create_bank_account_missing_name(test_db_session, test_user, test_bank_extern, mock_get_user):
    """Test that creating account without name returns error"""

    account_data = Bank_Account_create(
        uid=test_user.uid,
        name=None
    )

    result = create_bank_account(account_data, mock_get_user, test_db_session)

    assert "error" in result
    assert "Valeurs manquantes" in result["error"]


def test_create_secondary_account(test_db_session, test_user, test_bank_extern, mock_get_user):
    """Test creating a secondary (non-principal) account"""

    account_data = Bank_Account_create(
        uid=test_user.uid,
        name="Mon Compte Secondaire",
        is_principal=False
    )

    result = create_bank_account(account_data, mock_get_user, test_db_session)

    assert result is not None
    bank_account = result["bank_account"]
    assert bank_account.is_principal is False


def test_iban_generation_unique(test_db_session, test_user, test_bank_extern, mock_get_user):
    """Test that multiple accounts get different IBANs"""

    account_data_1 = Bank_Account_create(
        uid=test_user.uid,
        name="Compte 1"
    )

    account_data_2 = Bank_Account_create(
        uid=test_user.uid,
        name="Compte 2"
    )

    result_1 = create_bank_account(account_data_1, mock_get_user, test_db_session)
    result_2 = create_bank_account(account_data_2, mock_get_user, test_db_session)

    iban_1 = result_1["bank_account"].iban
    iban_2 = result_2["bank_account"].iban

    assert iban_1 != iban_2, "IBANs should be unique"


def test_get_bank_id_not_found(test_db_session):
    """Test that get_bank_id raises exception when bank is not found"""

    # Don't create the bank, so it won't be found
    with pytest.raises(HTTPException) as exc_info:
        get_bank_id(test_db_session)

    assert exc_info.value.status_code == 500
    assert "not found" in exc_info.value.detail


def test_get_bank_id_success(test_db_session, test_bank_extern):
    """Test that get_bank_id returns correct bank ID"""

    bank_id = get_bank_id(test_db_session)

    assert bank_id is not None
    assert bank_id == test_bank_extern.id


def test_create_account_with_initial_balance(test_db_session, test_user, test_bank_extern, mock_get_user):
    """Test creating account with custom initial balance"""

    account_data = Bank_Account_create(
        uid=test_user.uid,
        name="Compte avec Balance",
        balance=Decimal("1000.50")
    )

    result = create_bank_account(account_data, mock_get_user, test_db_session)

    bank_account = result["bank_account"]
    assert bank_account.balance == Decimal("1000.50")
