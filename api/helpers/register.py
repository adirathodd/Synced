from pydantic_core import PydanticCustomError
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
import datetime
import jwt
from dotenv import load_dotenv

def validate_password_complexity(password: str) -> str:
        """
        Enforce a minimum password complexity:
        - at least 8 characters
        - at least one uppercase letter
        - at least one lowercase letter
        - at least one digit
        - at least one special character
        """
        if len(password) < 8:
            raise PydanticCustomError('password.too_short', 'Password must be at least 8 characters long')
        if not any(c.isupper() for c in password):
            raise PydanticCustomError('password.uppercase', 'Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            raise PydanticCustomError('password.lowercase', 'Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            raise PydanticCustomError('password.digit', 'Password must contain at least one digit')
        if not any(c in '!@#$%^&*()-_=+[{]}\\|;:\'",<.>/?`~' for c in password):
            raise PydanticCustomError('password.special', 'Password must contain at least one special character')
        return password

def create_email_text(email: str) -> str:
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    data = {"email": email, "exp": expiration_time}
    token = jwt.encode(data, os.getenv('jwt_key'), algorithm=os.getenv('jwt_algo'))
    verification_link = f"http://localhost:8000/verify/{token}"

    email_text = f'''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Verification Email</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
        <style>
        body {{
            border-radius: 0;
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #FFFFFF;
            color: #000000;
        }}
        .email-container {{
            border-radius: 20px;
            max-width: 600px;
            margin: 0 auto;
            background-color: #3A3A3A;
            overflow: hidden;
        }}
        .header {{
            padding: 20px;
            text-align: center;
            background-color: #444444;
        }}
        .content {{
            padding: 20px;
            color: #E0E0E0;
        }}
        p {{
            line-height: 1.5;
            color: inherit;
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .cta-button {{
            background-color: #2c7a7b;
            color: #ffffff !important;
            padding: 15px 25px;
            text-decoration: none;
            font-size: 16px;
            border-radius: 20px;
            display: inline-block;
        }}
        .cta-button:hover {{
            background-color: #285e5f;
            color: #ffffff !important;
        }}
        .footer {{
            background-color: #444444;
            border-radius: 20px;
            text-align: center;
            padding: 10px;
            color: #888888;
            font-size: 12px;
        }}
        </style>
      </head>
      <body bgcolor="#FFFFFF" style="background-color: #FFFFFF !important;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#FFFFFF" style="background-color: #FFFFFF !important; border-collapse: collapse !important;">
          <tr>
            <td style="padding: 0; margin: 0;">
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