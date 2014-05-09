import tweepy

# Your application Twitter application ("consumer") key and secret.
# You'll need to register an application on Twitter first to get this
# information: http://www.twitter.com/oauth
APPLICATION_KEY = "wVNq8OD84WGCU4ly3wzeg"
APPLICATION_SECRET = "mhJMASHpNvbQUco9vIB8Eo04fzR9nQ7LCf5nH4dcHw"

# Fill in the next 2 lines after you have successfully logged in to 
# Twitter per the instructions above. This is the *user's* token and 
# secret. You need these values to call the API on their behalf after 
# they have logged in to your app.
USER_TOKEN = "49917710-IXh5cRQuV3LnkrFrmWkbbYauDfuaFmyQqki6Unvsa"
USER_SECRET = "DjYMzdjxmjM8IgghHMkWAnBBi220mdF5KyXKaIQbd3hht"

def get_client():
  tweepy_auth = tweepy.OAuthHandler(APPLICATION_KEY, APPLICATION_SECRET)
  tweepy_auth.set_access_token(USER_TOKEN, USER_SECRET)

  tweepy_api = tweepy.API(tweepy_auth)
  return tweepy_api

def get_public_tweets(tweepy_api=get_client()):

  home_timeline = tweepy_api.home_timeline()

  tweets = map( (lambda tweet: tweet.text),
                home_timeline)

  return tweets

def get_closest_woeid(lat,long,tweepy_api=get_client()):

  closest_locations = tweepy_api.trends_closest(lat,long)

  if len(closest_locations) is 1:
    return closest_locations[0]['woeid']
  else:
    return None


def get_closest_trends(lat,long,tweepy_api=get_client()):

  trends = tweepy_api.trends_place(
                        get_closest_woeid(lat,long,tweepy_api))

  trends = reduce( (lambda all_trends ,location:
                      all_trends + location['trends']),
                   trends,[])
  return trends


