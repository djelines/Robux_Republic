import os
import sys
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("FATAL: SECRET_KEY manquant", file=sys.stderr)
    sys.exit(1)

ALGORITHM = os.getenv("ALGORITHM", "HS256")
DB_NAME = os.getenv("DB_NAME" ,"database.db")
BANK_NAME = os.getenv("BANK_NAME" ,"Robux")
IS_PROD = os.getenv("IS_PROD", "false").lower() == "true"
CEILING_ACCOUNT = int(os.getenv("CEILING_ACCOUNT", 50000))

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