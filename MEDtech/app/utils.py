from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message

# Function to generate a verification token
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification-salt')

# Function to confirm the verification token
def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification-salt',
            max_age=expiration
        )
    except Exception:
        return None
    return email

# Function to send the verification email
def send_verification_email(email, verification_url):
    print("entering send verification")
    print(email)
    mail = current_app.extensions.get('mail')  # Access the initialized mail instance
    msg = Message(
        subject='Verify Your Email',
        sender='dija.aa1714@gmail.com',
        recipients=[email]
    )
    msg.body = f'Please click the link to verify your email: {verification_url}'
    mail.send(msg)
    print("finished send verification")
