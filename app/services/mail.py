from fastapi import APIRouter, FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from app.settings.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME, MAIL_STARTTLS, MAIL_SSL_TLS, USE_CREDENTIALS, VALIDATE_CERTS

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME, 
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_FROM = MAIL_FROM,
    MAIL_PORT = MAIL_PORT,
    MAIL_SERVER = MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS = MAIL_STARTTLS,
    MAIL_SSL_TLS = MAIL_SSL_TLS,
    USE_CREDENTIALS =  USE_CREDENTIALS,
    VALIDATE_CERTS = VALIDATE_CERTS
)



from fastapi_mail import MessageSchema 


async def simple_send(email: EmailSchema, message: str) -> JSONResponse:
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                color: #333;
                padding: 20px;
                border: 1px solid #007bff; /* Bordure bleue Robux */
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
            }}
            .header {{ 
                text-align: center; 
                padding-bottom: 15px;
                border-bottom: 3px solid #007bff;
                margin-bottom: 25px;
            }}
            .header h1 {{ 
                color: #007bff; /* Bleu vif */
                margin: 0;
                font-size: 24px;
            }}
            .content-box {{ 
                padding: 20px;
                background-color: #f7f7f7; /* Gris clair pour distinguer le message */
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            .content-box p {{
                margin: 0;
            }}
            .signature {{
                margin-top: 30px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>RobuxBank 🏦</h1>
            </div>
            
            <p>Cher client,</p>
            <p>Veuillez trouver ci-dessous l'information ou la notification demandée :</p>
            
            <div class="content-box">
                <p><strong>Détail du message :</strong></p>
                <p>{message}</p>
            </div>
            <div class="signature">
                <p>Cordialement,</p>
                <p>L'équipe Support RobuxBank</p>
            </div>
        </div>
    </body>
    </html>
    """
    

    message_schema = MessageSchema(
        subject="Notification de la RobuxBank",
        recipients=email.dict().get("email"),
        body=html_content,  
        subtype="html"    
    )

    fm = FastMail(conf)
    await fm.send_message(message_schema) 
    return JSONResponse(status_code=200, content={"message": "email has been sent"})