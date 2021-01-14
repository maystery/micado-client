import requests
from keystoneauth1.identity import v3

from micado import exceptions


class Authenticator:
    auth_url = None

    def authenticate(self):
        """ Returns a v3 auth object """
        raise NotImplementedError


class PasswordAuthenticator(Authenticator):
    def __init__(self, *, username, password):
        self.username = username
        self.password = password
        self.user_domain_name = "default"
        self.project_id = None

    def authenticate(self):
        """ Returns a Password auth object"""
        return v3.Password(
            self.auth_url,
            username=self.username,
            password=self.password,
            user_domain_name=self.user_domain_name,
            project_id=self.project_id,
        )


class OidcAuthenticator(Authenticator):
    def __init__(self, *, access_token, identity_provider, protocol="openid"):
        self.access_token = access_token
        self.identity_provider = identity_provider
        self.protocol = protocol
        self.project_id = None

    def authenticate(self):
        """ Returns an OidcAccessToken auth object"""
        return v3.OidcAccessToken(
            self.auth_url,
            protocol=self.protocol,
            access_token=self.access_token,
            identity_provider=self.identity_provider,
            project_id=self.project_id,
        )


class AppCredAuthenticator(Authenticator):
    def __init__(
        self, *, application_credential_id, application_credential_secret
    ):
        self.application_credential_id = application_credential_id
        self.application_credential_secret = application_credential_secret

    def authenticate(self):
        """ Returns an ApplicationCredential auth object"""
        return v3.ApplicationCredential(
            self.auth_url,
            application_credential_id=self.application_credential_id,
            application_credential_secret=self.application_credential_secret,
        )


def refresh_openid_token(
    *,
    url,
    client_id,
    client_secret,
    refresh_token,
    grant_type="refresh_token",
    scope="openid email profile",
):
    """ Returns a new OpenID access token """
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "refresh_token": refresh_token,
        "scope": scope,
    }

    try:
        response = requests.post(
            url, data=body, auth=(client_id, client_secret)
        ).json()
        return response["access_token"]
    except KeyError:
        raise exceptions.MicadoException("OpenID failed: {response}")


PRIMARY_AUTH_TYPES = (
    PasswordAuthenticator,
    AppCredAuthenticator,
    OidcAuthenticator,
)

PRE_AUTH_TYPES = {
    "OPENID": refresh_openid_token,
}