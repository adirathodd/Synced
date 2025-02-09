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
        items = item.model_dump()

        # Validate email address
        if not re.search(r'[\w.]+\@[\w.]+', items['email']):
            return {"message": "invalid email address"}
        
        # validate middle name field
        items['middle_name'] = None if len(items['middle_name'].strip()) == 0 else items['middle_name']

        # Encrypt password
        items['password'] = fernet.encrypt(items['password'].encode()).decode()
        
        # Add user to database
        res, message = db.create_user(items)

        if not res:
            if 'duplicate key' in message:
                paren_start = None; paren_end = None
                for idx, char in enumerate(message):
                    if char == '(':
                        paren_start = idx
                    elif char == ')':
                        paren_end = idx
                        break
                taken_field = message[paren_start+1:paren_end]
                message = f"{taken_field} already taken"

            return {"message": message}
        
        # Send verification email
        res = send_verification_email(items['email'])

        if not res:
            db.delete_user(email=items['email'])
            return {"message": "unable to send verification email try a diff email"}

        return {"message": "check email for verification link"}

    except Exception as e:
        print(str(e))
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
        print(str(e))
        return {"message": "invalid verification link"}

class LoginItem(BaseModel):
    username: str
    password: str

# 1 = success, -1 = wrong password, -2 = unknown username, 0 = something went wrong
@app.post("/login")
async def login(item: LoginItem):
    try:
        items = item.model_dump()

        # check password in database
        check = db.check_password(items['username'], items['password'])

        if check == -1:
            return {"message": "wrong password"}
        elif check == -2:
            return {"message": "unknown username"}  
        elif check == 0:
            return {"message": "something went wrong. try again"}  
            
        return {"message": "logged in!"}
    except Exception as e:
        print(str(e))
        return {"message": f"login failed"}

@app.get("/")
async def root():
    return {"message": "Hello World"}