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

"""Request Handler for /signout endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import webapp2

from google.appengine.api import urlfetch

from model import Credentials
import util


OAUTH2_REVOKE_ENDPOINT = 'https://accounts.google.com/o/oauth2/revoke?token=%s'


class SignoutHandler(webapp2.RequestHandler):
  """Request Handler for the signout endpoint."""

  @util.auth_required
  def post(self):
    """Delete the user's credentials from the datastore."""
    urlfetch.fetch(OAUTH2_REVOKE_ENDPOINT % self.credentials.refresh_token)
    util.store_userid(self, '')
    credentials_entity = Credentials.get_by_key_name(self.userid)
    if credentials_entity:
      credentials_entity.delete()
    self.redirect('/')


SIGNOUT_ROUTES = [
    ('/signout', SignoutHandler)
]
