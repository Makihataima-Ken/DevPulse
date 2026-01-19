from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth as firebase_auth


class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication using Firebase ID Tokens
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None  # No auth header → DRF will move on

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid Authorization header format")

        id_token = auth_header.split("Bearer ")[1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except Exception:
            raise AuthenticationFailed("Invalid or expired Firebase token")

        # Minimal "user" object (we don’t use Django User model)
        uid = decoded_token.get("uid")

        if not uid:
            raise AuthenticationFailed("Invalid Firebase token payload")

        # DRF expects (user, auth)
        return (FirebaseUser(uid), None)


class FirebaseUser:
    """
    Minimal user object for DRF
    """

    def __init__(self, uid):
        self.uid = uid
        self.is_authenticated = True

    def __str__(self):
        return self.uid