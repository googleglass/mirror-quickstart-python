# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for the Quickstart."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


from urlparse import urlparse

import httplib2
from apiclient.discovery import build
from oauth2client.appengine import StorageByKeyName
import sessions

from model import Credentials


# Load the secret that is used for client side sessions
# Create one of these for yourself with, for example:
# python -c "import os; print os.urandom(64)" > session.secret
SESSION_SECRET = open('session.secret').read()


def get_full_url(request_handler, path):
  """Return the full url from the provided request handler and path."""
  pr = urlparse(request_handler.request.url)
  return '%s://%s%s' % (pr.scheme, pr.netloc, path)


def load_session_credentials(request_handler):
  """Load credentials from the current session."""
  session = sessions.LilCookies(request_handler, SESSION_SECRET)
  userid = session.get_secure_cookie(name='userid')
  if userid:
    return userid, StorageByKeyName(Credentials, userid, 'credentials').get()
  else:
    return None, None


def store_userid(request_handler, userid):
  """Store current user's ID in session."""
  session = sessions.LilCookies(request_handler, SESSION_SECRET)
  session.set_secure_cookie(name='userid', value=userid)


def create_service(service, version, creds=None):
  """Create a Google API service.

  Load an API service from a discovery document and authorize it with the
  provided credentials.

  Args:
    service: Service name (e.g 'mirror', 'oauth2').
    version: Service version (e.g 'v1').
    creds: Credentials used to authorize service.
  Returns:
    Authorized Google API service.
  """
  # Instantiate an Http instance
  http = httplib2.Http()

  if creds:
    # Authorize the Http instance with the passed credentials
    creds.authorize(http)

  return build(service, version, http=http)


def auth_required(handler_method):
  """A decorator to require that the user has authorized the Glassware."""

  def check_auth(self, *args):
    self.userid, self.credentials = load_session_credentials(self)
    self.mirror_service = create_service('mirror', 'v1', self.credentials)
    # TODO: Also check that credentials are still valid.
    if not self.credentials:
      self.redirect('/auth')
      return
    else:
      handler_method(self, *args)
  return check_auth
