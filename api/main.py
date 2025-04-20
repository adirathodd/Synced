from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os
from helpers.util import create_access_token
from helpers.register import send_verification_email, validate_password_complexity
import jwt
from helpers.user import UserManager
from datetime import timedelta
import logging

load_dotenv()

logger = logging.getLogger(__name__)

userManager = UserManager()
app = FastAPI()

# load environment variables
SECRET_KEY = os.getenv("jwt_key")
ALGORITHM = os.getenv("jwt_algo")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class RegisterItem(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    username: str
    password: str

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and 'error' in detail and 'message' in detail:
        content = detail
    else:
        content = {"error": "error", "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=content) 

@app.post("/register", status_code=201)
async def register(item: RegisterItem, background_tasks: BackgroundTasks):
    try:
        items = item.dict()

        validate_password_complexity(items['password'])
        userManager.add_user(items)
        
        # schedule sending verification email in the background
        background_tasks.add_task(send_verification_email, items['email'])

        return {"message": "check email for verification link"}

    except Exception as e:
        logger.error("Error in registration: %s", e)
        raise HTTPException(status_code=400, detail=e)

@app.get("/verify/{token}")
async def verify(token: str):
    try:
        # decode the token and retrieve the email
        decoded_token = jwt.decode(token, os.getenv('jwt_key'), algorithms=os.getenv('jwt_algo'),  options={"verify_exp": True})

        # update table in database
        userManager.verify_email(decoded_token['email'])
        return {"message": "your email has been verified!"}

        # link has expried
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400,detail={"error": "link_expired", "message": "Verification link has expired. Please register again."})
    
    except Exception as e:
        logger.error("Error in verification: %s", e)
        raise HTTPException(status_code=400,detail={"error": "invalid_token", "message": "Invalid verification link."})

class LoginItem(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(item: LoginItem):
    try:
        items = item.model_dump()

        # check password in database
        userManager.verify(items['username'], items['password'])
        access_token = create_access_token(
            data={"sub": item.username},
            expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error("Error in login: %s", e)
        raise HTTPException(status_code=500, detail={"error": "server_error", "message": f"{str(e)}"})

@app.get("/")
async def root():
    return {"message": "Hello World"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT bearer token and return the username."""
    credentials_exception = HTTPException(status_code=401,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

##################### Protected Routes (Logged in) #####################

