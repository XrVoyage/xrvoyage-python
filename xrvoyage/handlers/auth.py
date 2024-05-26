from abc import ABC, abstractmethod
import time

import jwt
import requests
import logzero

from xrvoyage.common.config import get_app_config
from xrvoyage.common.exceptions import InvalidCredentialsError


def _is_token_expired(token: str) -> bool:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get('exp', 0)
        current_time = time.time()
        if current_time > exp or current_time >= (exp - 60):
            return True
        return False
    except Exception as e:
        logzero.logger.debug('Token could not be decoded', e)
        raise InvalidCredentialsError('Could not decode token')


class TokenStrategy(ABC):
    @abstractmethod
    def   get_token(self):
        raise NotImplementedError


class _AccessAndSecretKeyTokenStrategy(TokenStrategy):
    def __init__(self):
        self._access_token = None
        self._refresh_token = None

    def _login(self):
        settings = get_app_config()
        credentials = {
            "access_key": settings.XRVOYAGE_ACCESS_KEY_ID,
            "secret_key": settings.XRVOYAGE_SECRET_ACCESS_KEY
        }
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/oidc/login'
        response = requests.post(url, json=credentials)

        if not response.ok:
            raise InvalidCredentialsError(msg='Invalid access or secret key.')

        raw_data = response.json()
        self._access_token = raw_data['access_token']
        self._refresh_token = raw_data['refresh_token']

    def _refresh_access_token(self):
        credentials = {
            "refresh_token": self._refresh_token
        }
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/oidc/refresh'
        response = requests.post(url, json=credentials)

        if not response.ok:
            raise InvalidCredentialsError(msg='Could not refresh access token')

        raw_data = response.json()
        self._access_token = raw_data['access_token']
        self._refresh_token = raw_data['refresh_token']

    def get_token(self):

        if self._refresh_token is None or _is_token_expired(self._refresh_token):
            self._login()

        if _is_token_expired(self._access_token):
            try:
                self._refresh_access_token()
            except InvalidCredentialsError:
                logzero.logger.debug('Failed to refresh access token. Attempting to login ...')
                self._login()

        return self._access_token


class _TemporaryTokenStrategy(TokenStrategy):
    def get_token(self):
        settings = get_app_config()
        token = settings.XRVOYAGE_SESSION_TOKEN
        if _is_token_expired(token):
            raise InvalidCredentialsError('The provided XRVOYAGE_SESSION_TOKEN is expired.')
        return token


def _check_credentials():
    settings = get_app_config()
    cred_envs = [
        settings.XRVOYAGE_SESSION_TOKEN,
        settings.XRVOYAGE_SECRET_ACCESS_KEY,
        settings.XRVOYAGE_ACCESS_KEY_ID
    ]

    none_provided_cond = all([value is None for value in cred_envs])
    all_provided_cond = all([value is not None for value in cred_envs])
    tmp_token_provided_cond = all([
        settings.XRVOYAGE_SESSION_TOKEN is not None,
        settings.XRVOYAGE_ACCESS_KEY_ID is None,
        settings.XRVOYAGE_SECRET_ACCESS_KEY is None
    ])
    access_secret_key_provided_cond = all([
        settings.XRVOYAGE_SESSION_TOKEN is None,
        settings.XRVOYAGE_ACCESS_KEY_ID is not None,
        settings.XRVOYAGE_SECRET_ACCESS_KEY is not None
    ])
    message = """
        Provide either:-

        XRVOYAGE_SESSION_TOKEN 

        or 

        XRVOYAGE_SECRET_ACCESS_KEY
        XRVOYAGE_ACCESS_KEY_ID
    """
    creds_error = InvalidCredentialsError(message)

    if none_provided_cond or all_provided_cond:
        raise creds_error

    if not tmp_token_provided_cond and not access_secret_key_provided_cond:
        raise creds_error


def get_token_strategy() -> TokenStrategy:
    _check_credentials()

    settings = get_app_config()
    if settings.XRVOYAGE_SESSION_TOKEN is not None:
        return _TemporaryTokenStrategy()

    return _AccessAndSecretKeyTokenStrategy()
