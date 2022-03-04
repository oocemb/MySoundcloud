from datetime import datetime
from typing import Optional
from django.conf import settings
import jwt
from rest_framework import authentication, exceptions

from ..models import AuthUser



class AuthBackend(authentication.BaseAuthentication):
    """Аутентификация пользователя по токену JWT на бэкэнде"""
    authentication_header_prefix = 'Token'
    def authenticate(self, request, token=None, **kwargs) -> Optional[tuple]:
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower != b'token':
            return None

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credential provided.')
        elif len(auth_header) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string not contain spaces.')

        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string not contain invalid characters.')
        
        return self.authenticate_credential(token)

    def authenticate_credential(self, token) -> tuple:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except jwt.PyJWKError:
            raise exceptions.AuthenticationFailed('Invalid authentication. jwt not decode token.')
        
        token_exp = datetime.fromtimestamp(payload['exp'])
        if token_exp < datetime.utcnow():
            raise exceptions.AuthenticationFailed('Token expired.')
        
        try:
            user = AuthUser.objects.get(id=payload['user_id'])
        except AuthUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('No user matching this token was found.')
        return user, None
