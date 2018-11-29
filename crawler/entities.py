import os
import sys
import json
from twython import Twython
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class   Tweet(Base):
    __tablename__ = 'tweet'
    
    id = Column(Integer, primary_key=True)
    hashtag = Column(String(280), nullable=False)
    user = Column(String(280), nullable=False)
    date = Column(String(280), nullable=False)
    content = Column(String(300), nullable=False)
    favorite = Column(Integer)
        
class Hashtag():
    def __init__(self, name, lang='en', resulType='popular', nb=10):
        self.name = name
        self.lang = lang
        self.nb = nb
        self.resulType = resulType
        self.query = {}
        self.date = datetime.now()
        
    def createQuery(self):
       self.query = {
           'q': self.name,
           'count': self.nb,
           'lang': self.lang,
       }
       if self.resulType :
           self.query['result_type'] = self.resulType

    def sendQuery(self, python_tweets, session):
        for status in python_tweets.search(**self.query)['statuses']:
            tweet = Tweet(hashtag=self.name,
                          user=status['user']['screen_name'],
                          date=status['created_at'],
                          content=status['text'],
                          favorite=status['favorite_count']
            )
            session.add(tweet)
            session.commit() ## Voir a faire un commit tous les X tweets

    def getTweets(self, session):
        return session.query(Tweet).filter(Tweet.hashtag == self.name).all()

    def getTweetsList(self, session):
        return [{'user':elem.user, 'date':elem.date, 'content':elem.content, 'favorite':elem.favorite} for elem in self.getTweets(session)]

    def erease(self, session):
        session.query(Tweet).filter(Tweet.hashtag == self.name).delete()
        session.commit()
    
class   Crawler():
    def __init__(self, path='crawler.json'):
        with open(path, 'r') as file:
            self.conf = json.load(file)
        self.python_tweets = Twython(self.conf['CONSUMER_KEY'], self.conf['CONSUMER_SECRET'])
        self.hashtag = {}
        
    def linkDB(self):
        engine = create_engine(self.conf['DB_SQLITE_ACCESS'])
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def addHashtag(self, hashtag):
        self.hashtag[hashtag.name] = hashtag

    def delHashtag(self, hashtag, session):
        if hashtag in self.hashtag:
            self.hashtag[hashtag].erease(session)
            del self.hashtag[hashtag]
        
    def getHashtag(self, hashtagtitle, session):
        if hashtagtitle in self.hashtag:
            result = self.hashtag[hashtagtitle]
            diff = datetime.now() - result.date
            if divmod(diff.days * 86400 + diff.seconds, 60)[0] >= 1:
                self.delHashtag(hashtagtitle, session)
                result = None
            return result
        return None

## Create db and table
crawler = Crawler()
engine = create_engine(crawler.conf['DB_SQLITE_ACCESS'])
Base.metadata.create_all(engine)
