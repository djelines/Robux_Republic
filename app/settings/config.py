import os
from dotenv import load_dotenv
load_dotenv()

DB_NAME = os.getenv("DB_NAME" ,"database.db")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY" ,"default_secret_key")
BANK_NAME = os.getenv("BANK_NAME" ,"Robux")
CEILING_ACCOUNT = os.getenv("CEILING_ACCOUNT", 50000)

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Robux Republic")

MAIL_PORT = int(os.getenv("MAIL_PORT", 465))

MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "False").lower() == "true"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "True").lower() == "true"
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS", "True").lower() == "true"
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS", "True").lower() == "true"