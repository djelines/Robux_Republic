import uuid
from passlib.context import CryptContext


pdw_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Var global 


def generate_uid() -> str:
    """ Generate a unique identifier (UID) using UUID4."""
    return str(uuid.uuid4())

def generate_iban() -> str:
    """ Generate a pseudo-random IBAN for demonstration purposes."""
    return "FR76" + str(uuid.uuid4().int)[:20] + "RobuxCommunity"  

def hash_password(password: str) -> str:
    """ Hash a plain password using Passlib's CryptContext."""
    return pdw_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verify a plain password against a hashed password."""
    return pdw_context.verify(plain_password, hashed_password)
