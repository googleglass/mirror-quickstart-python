import tweepy

import webapp2
from oauth2client.appengine import StorageByKeyName
from google.appengine.api import memcache

import logging

from model import Credentials

import util

# Your application Twitter application ("consumer") key and secret.
# You'll need to register an application on Twitter first to get this
# information: http://www.twitter.com/oauth
APPLICATION_KEY = "wVNq8OD84WGCU4ly3wzeg"
APPLICATION_SECRET = "mhJMASHpNvbQUco9vIB8Eo04fzR9nQ7LCf5nH4dcHw"

def get_twitter_creds(userid):
  key = StorageByKeyName(Credentials, userid, 'twitter_oauth_token_key').get()
  secret = StorageByKeyName(Credentials, userid, 'twitter_oauth_token_secret').get()
  oauth_verifier = StorageByKeyName(Credentials, userid, 'twitter_oauth_verifier').get()
  access_token = StorageByKeyName(Credentials, userid, 'twitter_access_token').get()
  access_secret = StorageByKeyName(Credentials, userid, 'twitter_access_secret').get()

  creds = (key,secret,oauth_verifier,access_token,access_secret)
  return creds

def set_twitter_creds(userid,token_key,token_secret,oauth_verifier=None,access_token=None, access_secret=None):

  StorageByKeyName(Credentials, userid, 'twitter_oauth_token_key').put(token_key)
  StorageByKeyName(Credentials, userid, 'twitter_oauth_token_secret').put(token_secret)
  StorageByKeyName(Credentials, userid, 'twitter_oauth_verifier').put(oauth_verifier)
  StorageByKeyName(Credentials, userid, 'twitter_access_token').put(access_token)
  StorageByKeyName(Credentials, userid, 'twitter_access_secret').put(access_secret)



def get_auth(callback_url=None):
    return tweepy.OAuthHandler(APPLICATION_KEY, APPLICATION_SECRET,callback_url)

def get_client(userid):
  tweepy_auth = get_auth()
  key,secret,oauth_verifier,access_token,access_secret= get_twitter_creds(userid)

  if oauth_verifier is None:
    return None

  tweepy_auth.set_access_token(access_token,access_secret)

  tweepy_api = tweepy.API(tweepy_auth)
  return tweepy_api

def get_auth_uri(callback_url):
  tweepy_auth = get_auth(callback_url)
  uri = tweepy_auth.get_authorization_url()
  request_token = tweepy_auth.request_token
  return (tweepy_auth.request_token.key, tweepy_auth.request_token.secret, uri)

def get_public_tweets(tweepy_api):
  home_timeline = tweepy_api.home_timeline()
  tweets = map( (lambda tweet: tweet.text),
                home_timeline)
  return tweets

def get_closest_woeid(lat,long,tweepy_api):
  closest_locations = tweepy_api.trends_closest(lat,long)

  if len(closest_locations) is 1:
    return closest_locations[0]['woeid']
  else:
    return None


def get_closest_trends(lat,long,tweepy_api):

  trends = tweepy_api.trends_place(
                        get_closest_woeid(lat,long,tweepy_api))

  trends = reduce( (lambda all_trends ,location:
                      all_trends + location['trends']),
                   trends,[])
  return trends

def is_authorized(userid,mirror_service):
  tweepy_api = get_client(userid)
  is_authorized = tweepy_api is not None
  return is_authorized


class TwitterCallbackHandler(webapp2.RequestHandler):
  """Callback called by twitter authentication"""

  def get(self):
    """Get the user's oauth info"""
    oauth_token = self.request.get("oauth_token", None)
    oauth_verifier = self.request.get("oauth_verifier", None)

    userid = util.load_session_userid(self)

    (key,secret,_,_,_) = get_twitter_creds(userid)
    assert oauth_token == key

    tweepy_auth = get_auth()
    tweepy_auth.set_request_token(key,secret)

    access = tweepy_auth.get_access_token(oauth_verifier)
    set_twitter_creds(userid,key,secret,oauth_verifier,access.key,access.secret)
    self.redirect('/')

  @util.auth_required
  def post(self):
    """Execute the request and render the template."""
    operation = self.request.get('operation')
    # Dict of operations to easily map keys to methods.
    operations = {
        'insertTrends': self._insert_trends
    }
    if operation in operations:
      message = operations[operation]()
    else:
      message = "I don't know how to " + operation
    # Store the flash message for 5 seconds.
    memcache.set(key=self.userid, value=message, time=5)
    self.redirect('/')

  def _insert_trends(self):
    """Insert the trends closest to the user"""

    lat,long = 40,-73
    try:
      location = self.mirror_service.locations().get(id='latest').execute()
      lat,long = location.get('latitude'), location.get('longitude')
    except:
      lat,long = 40,-73

    logging.debug(lat,long)

    userid = util.load_session_userid(self)

    tweepy_api = get_client(userid)

    trends = get_closest_trends(lat,long,
                          tweepy_api)

    summary = reduce ( (lambda summary,trend: summary + trend['name'] + "\n"),
                       trends,"")

    body = {
        'notification': {'level': 'DEFAULT'},
        'text' : summary
    }

    # self.mirror_service is initialized in util.auth_required.
    self.mirror_service.timeline().insert(body=body).execute()
    return 'Application is now subscribed to twitter.'


TWITTER_CALLBACK_LINK = '/twitter_oauth2callback'
TWITTER_ROUTES = [ 
    (TWITTER_CALLBACK_LINK, TwitterCallbackHandler),
    ('/twitter', TwitterCallbackHandler),
    ]
