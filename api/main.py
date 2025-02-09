from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
import re
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from helpers.database import Database
from helpers.utils import send_verification_email
import jwt
from starlette.responses import RedirectResponse

load_dotenv()

db = Database()
app = FastAPI()
fernet = Fernet(os.getenv('fernet_key'))

class RegisterItem(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    username: str
    password: str

@app.post("/register")
async def register(item: RegisterItem):
    try:
        item_dict = item.model_dump()

        # Validate email address
        if not re.search(r'[\w.]+\@[\w.]+', item_dict['email']):
            return {"message": "invalid email address"}
        
        email = item_dict['email']; username = item_dict['username']

        # Encrypt password
        item_dict['password'] = fernet.encrypt(item_dict['password'].encode())
        
        # Add user to database
        res, message = db.create_user(item_dict)

        if not res:
            return {"message": message}
        
        # Send verification email
        res = send_verification_email(email)

        if not res:
            db.delete_user(email=item_dict['email'])
            return {"message": "unable to send verification email try a diff email"}

        return {"message": "check email for verification link"}

    except Exception as e:
        print(e)
        return {"message": "something went wrong. try again"}

@app.get("/verify/{token}")
async def verify(token: str):
    try:
        # decode the token and retrieve the email
        decoded_token = jwt.decode(token, os.getenv('jwt_key'), algorithms=os.getenv('jwt_algo'),  options={"verify_exp": True})

        # update table in database
        res, message = db.verify_email(decoded_token['email'])

        if not res:
            message = "failed to verify your email"
        else:
            message = "your email has been verified!"

        return {"message": message}

        # link has expried
    except jwt.ExpiredSignatureError:
        return {"message": "verification link has expired. register again"}
    except Exception as e:
        print(e)
        return {"message": "invalid verification link"}

class LoginItem(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(item: LoginItem):
    return {"message": "logged in!"}

@app.get("/")
async def root():
    return {"message": "Hello World"}