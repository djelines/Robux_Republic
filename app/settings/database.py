from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from app.settings.config import DB_NAME

if DB_NAME.startswith("sqlite:///"):
    sqlite_url = DB_NAME
else:
    sqlite_url = f"sqlite:///{DB_NAME}"
    
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
     
def get_session():
    with Session(engine) as session:
        yield session