from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
import re
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from helpers.database import Database
from helpers.utils import send_verification_email

load_dotenv()

class RegisterItem(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    username: str
    password: str

db = Database()
app = FastAPI()
fernet = Fernet(os.getenv('fernet_key'))

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
        return {"message": f"something went wrong: {e}"}

@app.post("/login")
async def login():
    return {"message": "logged in!"}

@app.get("/")
async def root():
    return {"message": "Hello World"}