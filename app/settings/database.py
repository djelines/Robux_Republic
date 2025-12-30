import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME", "database.db")

if not DATABASE_URL:
    if DB_NAME.startswith("sqlite:///"):
        DATABASE_URL = DB_NAME
    else:
        DATABASE_URL = f"sqlite:///{DB_NAME}"


connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# --- FONCTIONS ---
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
     
def get_session():
    with Session(engine) as session:
        yield session

