from sqlmodel import SQLModel, create_engine, Session
from app.settings.config import DB_NAME
 
 
if DB_NAME.startswith("sqlite:///"):
    sqlite_url = DB_NAME
else:
    sqlite_url = f"sqlite:///{DB_NAME}"
    
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """Create database and tables based on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)
     
def get_session():
    with Session(engine) as session:
        yield session
        

        