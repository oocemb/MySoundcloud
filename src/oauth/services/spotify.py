import base64
from multiprocessing import AuthenticationError
from typing import Optional
import requests
from django.conf import settings
from . import base_auth
from ..models import AuthUser


def get_spotify_jwt(code: str):
    """Запрашивает Спотифай access токен по заголовку Аутх"""
    url = 'https://accounts.spotify.com/api/token'
    basic_str = f'{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_SECRET_KEY}'.encode('ascii')
    basic = base64.b64encode(basic_str)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8000/spotify-callback'
    }
    headers = {
        'Authorization': f'Basic {basic.decode("ascii")}'
        ,'Content-Type': 'application/x-www-form-urlencoded'
    }

    print(res)
    res = requests.post(url, data=data, headers=headers)
    print(res.status_code)
    if res.status_code == 200:
        r = res.json()
        print(r.get('access_token'))
        return r.get('access_token')
    else: 
        return None


def get_spotify_user(token: str) -> str:
    url_get_user = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(url_get_user, headers=headers)
    r = res.json()
    return r.get('email')


def get_spotify_email(code: str) -> Optional[str]:
    _token = get_spotify_jwt(code)
    if _token is not None:
        return get_spotify_user(_token)
    else:
        return None


def spotify_auth(code: str):
    """Запрашивает информацию о пользователе Спотифай"""
    email = get_spotify_email(code)
    if email is not None:     
        user, _ = AuthUser.objects.get_or_create(email=email)
        return base_auth.create_token(user.id)
    else:
        raise AuthenticationError(code=403, detail='Bad token Spotify')