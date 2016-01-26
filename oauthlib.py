import urllib

# ROOT = 'https://drchrono.com/'
ROOT = 'http://drchrono.dev/'


def url(path):
    """Return url with path at rooted at domain root."""
    return ROOT + path.lstrip('/')

AUTH_URL = url('/o/authorize/')
TOKEN_URL = url('/o/token/')
REVOKE_URL = url('/o/revoke_token/')


def make_redirect(redirect_uri, client_id, scope):
    """Make redirect URI for OAuth."""
    return ''.join((
        AUTH_URL,
        "?redirect_uri={}",
        "&response_type=code",
        "&client_id={}",
        "&scope={}",
    )).format(
        urllib.quote_plus(redirect_uri),
        urllib.quote_plus(client_id),
        urllib.quote_plus(scope),
    )
