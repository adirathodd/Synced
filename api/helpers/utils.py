import mimetypes

def get_mime_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type

def is_image(filepath):
    mime_type = get_mime_type(filepath)
    return mime_type is not None and mime_type.startswith('image')

def is_video(filepath):
    mime_type = get_mime_type(filepath)
    return mime_type is not None and mime_type.startswith('video')

users_uniq = ['id', 'username', 'email']
users_req = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
users_opt = ['middle_name']
users_cols = set(users_opt + users_req)

files_uniq = ['storage_id']
files_req = ['storage_id', 'user_id', 'filename', 'filetype']
files_opt = ['uploaded_at']
files_cols = set(files_opt + files_req)