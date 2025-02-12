from .data import SCOPE
from requests_oauthlib import OAuth2Session

# import logger
from ..log_server import logger

LOCAL_HTTP_ADD = "http://localhost:4567"

PROXY = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# Define your SSO information
client_id = '002510ade64443bd829f035f6847d7e3'
secret_key = 'kevAXfIRW8hKfbdh2BQDlCWhfyDnBTUgpOuemkDb'
callback_url = LOCAL_HTTP_ADD + '/auth/eve/callback'

oauth = OAuth2Session(
    client_id=client_id,
    redirect_uri=callback_url,
    scope=SCOPE
)

def get_auth_url():
    authorizationUrl, state = oauth.authorization_url('http://login.eveonline.com/oauth/authorize')
    return authorizationUrl

def get_token(AUTH_RES):
    oauth.fetch_token(
        'https://login.eveonline.com/oauth/token',
        authorization_response=AUTH_RES,
        client_secret=secret_key,
        proxies=PROXY
    )

    access_token = oauth.token.get("access_token")
    refresh_token = oauth.token.get("refresh_token")
    expires_at = oauth.token.get("expires_at")

    return access_token, refresh_token, expires_at

def refresh_token(refresh_token):

    newtocker_dict = oauth.refresh_token(
        'https://login.eveonline.com/oauth/token',
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=secret_key,
        proxies=PROXY
    )

    logger.info(f"token refreshed. {newtocker_dict}")
    """
    {
        "access_token",
        "token_type",
        "expires_in", [second]
        "refresh_token",
        "expires_at"
    }
    """
    return newtocker_dict