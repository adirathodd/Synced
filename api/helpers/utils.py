import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
import jwt
from dotenv import load_dotenv

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
users_uniq = ['id', 'username', 'email']
users_req = ['username', 'email', 'password', 'first_name', 'last_name']
users_opt = ['middle_name', 'is_verified']
users_cols = set(users_opt + users_req)

files_uniq = ['file_id']
files_req = ['file_id', 'user_id', 'filename', 'filetype']
files_opt = ['uploaded_at']
files_cols = set(files_opt + files_req)

################ EMAIL ########################


def create_email_text(email: str) -> str:
    data = {"sub": email}
    token = jwt.encode(data, os.getenv('jwt_key'), algorithm=os.getenv('jwt_algo'))
    verification_link = f"https://localhost:8000/verify?token={token}"

    email_text = f'''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Verification Email</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          body {{
            border-radius: 100px;
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
          }}
          .email-container {{
            border-radius: 20px;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
          }}
          .header {{
            padding: 20px;
            text-align: center;
            background-color: #f0f5f5;
          }}
          .content {{
            padding: 20px;
            color: #333333;
          }}
          p {{
            line-height: 1.5;
          }}
          .button-container {{
            text-align: center;
            margin: 30px 0;
          }}
          .cta-button {{
            background-color: #2c7a7b;
            color: #ffffff;
            padding: 15px 25px;
            text-decoration: none;
            font-size: 16px;
            border-radius: 20px;
          }}
          .cta-button:hover {{
            background-color: #285e5f;
          }}
          .footer {{
            background-color: #f0f5f5;
            border-radius: 20px;
            text-align: center;
            padding: 10px;
            color: #888;
            font-size: 12px;
          }}
        </style>
      </head>
      <body>
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
          <tr>
            <td>
              <div class="email-container">        
                <div class="content">
                  <h2>Verify Your Email!</h2>
                  <p>
                    Thank you for joining the Synced community! In order to keep our community safe,
                    we ask users to verify their email after registering. Please click the button below
                    to verify your account.
                  </p>
                  <div class="button-container">
                    <a class="cta-button" href="{verification_link}" target="_blank">
                      Verify Email
                    </a>
                  </div>
                  <div class="footer">
                    <img src="cid:logo" alt="Company Logo" style="width:50px; height:auto; display:inline-block;">
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </table>
      </body>
    </html>
    '''
    
    return email_text

def send_verification_email(email):
  load_dotenv()

  server = "smtp.gmail.com"
  port = 587
  sender = os.getenv('email')
  password = os.getenv('email_password')

  if not email or not password:
      raise Exception("email credentials are not set in environment variables.")

  message = MIMEMultipart("related")
  message["Subject"] = "verify your synced email"
  message["From"] = "synced onboarding"
  message["To"] = email
  message.preamble = "This is a multi-part message in MIME format."

  # Create the alternative part for HTML content
  msg_alternative = MIMEMultipart('alternative')
  message.attach(msg_alternative)

  # Attach the HTML content
  html_content = create_email_text(email)
  msg_text = MIMEText(html_content, 'html')
  msg_alternative.attach(msg_text)

  try:
    with open("helpers/logo.JPG", "rb") as img_file:
        img_data = img_file.read()

    msg_image = MIMEImage(img_data)
    msg_image.add_header('Content-ID', '<logo>')
    msg_image.add_header('Content-Disposition', 'inline', filename="logo.JPG")
    message.attach(msg_image)

  except FileNotFoundError:
      print("Logo image file not found. Make sure 'logo.JPG' is in the correct location.")

  try:    
      with smtplib.SMTP(server, port) as server:
          server.starttls()
          server.login(sender, password)
          server.send_message(message)
      
      return True
  except Exception as e:
      print(e)
      return False