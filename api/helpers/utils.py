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