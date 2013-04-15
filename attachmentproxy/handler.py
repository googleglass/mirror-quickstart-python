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

"""Request Handler for /main endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import logging
import webapp2

from util import auth_required


class AttachmentProxyHandler(webapp2.RequestHandler):
  """Request Handler for the main endpoint."""

  @auth_required
  def get(self):
    """Return the attachment's content using the current user's credentials."""
    # self.mirror_service is initialized in util.auth_required.
    attachment_id = self.request.get('attachment')
    item_id = self.request.get('timelineItem')
    logging.info('Attachment ID: %s', attachment_id)
    if not attachment_id or not item_id:
      self.response.set_status(400)
      return
    else:
      # Retrieve the attachment's metadata.
      attachment_metadata = self.mirror_service.timeline().attachments().get(
          itemId=item_id, attachmentId=attachment_id).execute()
      content_type = str(attachment_metadata.get('contentType'))
      content_url = attachment_metadata.get('contentUrl')

      # Retrieve the attachment's content.
      resp, content = self.mirror_service._http.request(content_url)
      if resp.status == 200:
        self.response.headers.add_header('Content-type', content_type)
        self.response.out.write(content)
      else:
        logging.info('Unable to retrieve attachment: %s', resp.status)
        self.response.set_status(500)


ATTACHMENT_PROXY_ROUTES = [
    ('/attachmentproxy', AttachmentProxyHandler)
]
