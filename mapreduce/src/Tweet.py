from google.appengine.ext import db

class Tweet(db.Model):
    hashtag = db.StringProperty()
    user = db.StringProperty()
    date = db.StringProperty()
    content = db.StringProperty()
    favorite = db.IntegerProperty()

class TweetManager():
    
    @classmethod
    def getTweets(self, hashtag):
        query = Tweet.all()
        tweets = query.run()
        return tweets
