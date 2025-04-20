import mimetypes
import os
import datetime
import jwt

################ AWS HELPER ########################
def get_mime_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type

def is_image(filepath):
    mime_type = get_mime_type(filepath)
    return mime_type is not None and mime_type.startswith('image')

def is_video(filepath):
    mime_type = get_mime_type(filepath)
    return mime_type is not None and mime_type.startswith('video')

################ Database columns ################
users_req = ['username', 'email', 'password', 'first_name', 'last_name']
users_opt = ['middle_name']
users_cols = set(users_opt + users_req)

files_req = ['username', 'filename', 'file_ext', 'filepath']
files_opt = []
files_cols = set(files_opt + files_req)


######## LOGIN ################
def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    """Generate a JWT token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("jwt_key"), algorithm=os.getenv("jwt_algo"))