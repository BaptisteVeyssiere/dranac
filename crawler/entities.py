import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import json
from twython import Twython

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
        
    def createQuery(self):
       self.query = {
           'q': self.name,
           'count': self.nb,
           'lang': self.lang,
       }
       if self.resulType :
           self.query['reslut_type'] = self.resulType

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
        return session.query(Tweet).all()

    def getTweetsList(self, session):
        return [{'user':elem.user, 'date':elem.date, 'content':elem.content, 'favorite':elem.favorite} for elem in self.getTweets(session)]

class   Crawler():
    def __init__(self, path='crawler.json'):
        with open(path, 'r') as file:
            self.conf = json.load(file)
        self.python_tweets = Twython(self.conf['CONSUMER_KEY'], self.conf['CONSUMER_SECRET'])
        self.hashtag = {}
        
    def linkDB(self):
        engine = create_engine(self.conf['DB_ACCESS'])
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def addHashtag(self, hashtag):
        self.hashtag[hashtag.name] = hashtag
    
    def getHashtag(self, hashtagtitle):
        return self.hashtag.get(hashtagtitle, None)
            
    def delHashtag(self, hashtag):
        try:
            del hashtag[hashtag]
        except:
            pass
        
## Create db and table
crawler = Crawler()
engine = create_engine(crawler.conf['DB_ACCESS'])
Base.metadata.create_all(engine)
