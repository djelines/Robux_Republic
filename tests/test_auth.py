import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.settings.schemas import Auth
from app.models.models import get_db_engine
from app.settings.database import SQLModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

@pytest.fixture()
def test_db_session():
    """Create a new database session for testing."""
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
    """Create a test user in the database."""
    hashed_password = pwd_context.hash("testpassword")

    user = Auth(
        uid="testuid",
        email="test@gmail.com",
        password=hashed_password
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


def test_login_success(test_db_session, test_user):
    """Test successful login."""
    from app.services.auth import login


    user = login(
        test_user.email,
        "testpassword",
        test_db_session
    )
    assert user is not None , "Login failed when it should have succeeded"

