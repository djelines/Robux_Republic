import os
from dotenv import load_dotenv
load_dotenv()

DB_NAME = os.getenv("DB_NAME" ,"database.db")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY" ,"default_secret_key")
BANK_NAME = os.getenv("BANK_NAME" ,"Robux")
CEILING_ACCOUNT = os.getenv("CEILING_ACCOUNT", 50000)

 # Email configuration
    
MAIL_USERNAME= os.getenv("MAIL_USERNAME" ,"default")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD" ,"default")
MAIL_FROM =   os.getenv("MAIL_FROM" ,"default@gmail.com")
MAIL_PORT = os.getenv("MAIL_PORT" ,"587")
MAIL_SERVER = os.getenv("MAIL_SERVER" ,"default")
MAIL_FROM_NAME= os.getenv("MAIL_FROM_NAME" ,"default")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS","True")
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS","False")
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS","True")
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS","False")