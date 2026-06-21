from flask import current_app
from itsdangerous import URLSafeTimedSerializer

_RESET_SALT = 'password-reset'
_EMAIL_SALT = 'email-verify'


def _get_reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt=_RESET_SALT,
    )


def _get_email_serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt=_EMAIL_SALT,
    )


def generate_reset_token(user_id, expires_sec=3600):
    s = _get_reset_serializer()
    return s.dumps(str(user_id))


def verify_reset_token(token, max_age=3600):
    s = _get_reset_serializer()
    try:
        user_id = s.loads(token, max_age=max_age)
    except Exception:
        return None
    return user_id


def generate_email_token(user_id, expires_sec=86400):
    s = _get_email_serializer()
    return s.dumps(str(user_id))


def verify_email_token(token, max_age=86400):
    s = _get_email_serializer()
    try:
        user_id = s.loads(token, max_age=max_age)
    except Exception:
        return None
    return user_id
