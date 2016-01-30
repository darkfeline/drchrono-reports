# Copyright (C) 2016  Allen Li
#
# This file is part of drchrono-reports.
#
# drchrono-reports is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# drchrono-reports is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with drchrono-reports.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import json

from django.conf import settings

ROOT = 'https://drchrono.com/'


def get_secrets():
    """Load OAuth secrets and configuration."""
    with open(settings.DRCHRONO_REPORTS_SECRETS) as file:
        secrets = json.load(file)
    secrets['scope'] = 'patients user calendar'
    return secrets


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
