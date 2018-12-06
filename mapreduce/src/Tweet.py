import urllib2
import json
from collections import namedtuple

class TweetManager():
    
    @classmethod
    def getJson(self, hashtag):
        try:
            result = urllib2.urlopen("https://crawler-dot-corded-smithy-222417.appspot.com/v1.0/" + hashtag, timeout = 10)
        except urllib2.URLError, e:
            return False
        return result.read()

    @classmethod
    def jsonToTweets(self, json_content):
        tweets = json.loads(json_content, object_hook=lambda d: namedtuple('Tweet', d.keys())(*d.values()))
        return tweets
