# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime

# from twython import Twython
import tweepy 

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class   Tweet(Base):
    __tablename__ = 'tweet'
    
    id = Column(Integer, primary_key=True)
    hashtag = Column(String(300), nullable=False)
    user = Column(String(300), nullable=False)
    date = Column(String(300), nullable=False)
    content = Column(String(300), nullable=False)
    favorite = Column(Integer)
    embeddedTweet = Column(String(300))

class Hashtag():
    def __init__(self, name, lang='en', resulType='mixed', nb=100):
        self.name = name
        self.lang = lang
        self.nb = nb
        self.resulType = resulType
        self.query = {}
        self.date = datetime.now()
        self.until = '{:%Y-%m-%d}'.format(self.untilDate(datetime.now(), -10))

    def untilDate(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, [31, 29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date.replace(day=d,month=m, year=y)
    
    def createQuery(self):
        pass
       # self.query = {
       #     'q': self.name,
           # 'count': self.nb,
           # 'lang': self.lang,
           # 'tweet_mode': 'extended',
           # 'unitl': self.until
           # 'since_id': 10,
           # 'max_id': 100,
       # }
       # if self.resulType :
       #     self.query['result_type'] = self.resulType

    def sendQuery(self, api, session):
        save = 0
        for status in tweepy.Cursor(api.search, q=self.name, lang=self.lang, result_type=self.resulType, tweet_mode='extended').items(self.nb):
            if status.retweeted == False:
                tweet = Tweet(hashtag=self.name,
                              user=status.user.screen_name.encode('utf-8'),
                              date=status.created_at,
                              content=status.full_text.encode('utf-8'),
                              favorite=status.favorite_count,
                              embeddedTweet="https://publish.twitter.com/oembed?url=https://twitter.com/{}/status/{}".format(status.user.screen_name, status.id_str).encode('utf-8')
                )
            session.add(tweet)
            session.commit() ## Voir a faire un commit tous les X tweets

    def getTweets(self, session):
        return session.query(Tweet).filter(Tweet.hashtag == self.name).all()

    def getTweetsList(self, session):
        return [{'user':elem.user, 'date':elem.date, 'content':elem.content, 'favorite':elem.favorite, 'embeddedTweet': elem.embeddedTweet} for elem in self.getTweets(session)]

    def erease(self, session):
        session.query(Tweet).filter(Tweet.hashtag == self.name).delete()
        session.commit()
    
class   Crawler():
    def __init__(self, path='crawler.json'):
        with open(path, 'r') as file:
            self.conf = json.load(file)
        auth = tweepy.OAuthHandler(self.conf['CONSUMER_KEY'], self.conf['CONSUMER_SECRET'])
        auth.set_access_token(self.conf['ACCESS_TOKEN'], self.conf['ACCESS_SECRET'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.hashtag = {}
        
    def linkDB(self):
        engine = create_engine(self.conf['DB_ACCESS'])
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def addHashtag(self, hashtag, session, api, deadlineRequest):
        if hashtag.name in self.hashtag:
            result = self.hashtag[hashtag.name]
            diff = datetime.now() - result.date
            print("DEBUG:ADDHASHTAG:divmod:", divmod(diff.days * 86400 + diff.seconds, 60))
            if divmod(diff.days * 86400 + diff.seconds, 60)[0] >= deadlineRequest:
                print("DEBUG:ADDHASHTAG:delete hashtag min:", divmod(diff.days * 86400 + diff.seconds, 60)[0])
                self.delHashtag(hashtag.name, session)
                self.hashtag[hashtag.name] = hashtag
            else:
                print("DEBUG:ADDHASHTAG:nothing to do diff min:")   
        else:
            print("DEBUG:ADDHASHTAG:add hashtag")
            self.hashtag[hashtag.name] = hashtag
            hashtag.sendQuery(api, session)
                
    def delHashtag(self, hashtag, session):
        if hashtag in self.hashtag:
            self.hashtag[hashtag].erease(session)
            del self.hashtag[hashtag]
        
    def getHashtag(self, hashtagtitle, session):
        if hashtagtitle in self.hashtag:
            result = self.hashtag[hashtagtitle]
            # diff = datetime.now() - result.date
            # if divmod(diff.days * 86400 + diff.seconds, 60)[0] >= 30:
            #     self.delHashtag(hashtagtitle, session)
            #     result = None
            return result
        return None

## Create db and table
crawler = Crawler()
engine = create_engine(crawler.conf['DB_ACCESS'])
Base.metadata.create_all(engine)
