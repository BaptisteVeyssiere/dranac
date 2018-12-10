# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime

import tweepy 

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class   Tweet(Base):
    '''
    scheme in the SQL database.
    '''
    __tablename__ = 'tweet'
    
    id = Column(Integer, primary_key=True)
    hashtag = Column(String(3000), nullable=False)
    user = Column(String(3000), nullable=False)
    date = Column(String(3000), nullable=False)
    content = Column(String(5000), nullable=False)
    favorite = Column(Integer)
    embeddedTweet = Column(String(4000))

class Hashtag():
    '''
    Each hashtag search has it own Hashtag class
    
    '''
    def __init__(self, name, lang='en', resulType='mixed', nb=100):
        self.name = name
        self.lang = lang
        self.nb = nb
        self.resulType = resulType
        self.query = {}
        self.date = datetime.now()
        self.since = '{:%Y-%m-%d}'.format(self.sinceDate(datetime.now(), -10))

        '''
        Feature to substract X month to the actual date. In order to allow user to choose filter the search action
        (not add to the actual service)
        '''
    def sinceDate(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, [31, 29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date.replace(day=d,month=m, year=y)

    '''
    Send the query to the Twitters API and register them into the SQLserver
    '''
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
            session.commit() ## TODO: commit only every X turns of the loop

    '''
    Search for all the tweet relative to this hashtag on the DB
    '''
    def getTweets(self, session):
        return session.query(Tweet).filter(Tweet.hashtag == self.name).all()

    '''
    Return a <class 'list'> of <class 'dict'> to serialize the data
    '''
    def getTweetsList(self, session):
        return [{'user':elem.user, 'date':elem.date, 'content':elem.content, 'favorite':elem.favorite, 'embeddedTweet': elem.embeddedTweet} for elem in self.getTweets(session)]

    '''
    delete the Hashtag on DB
    '''
    def erease(self, session):
        session.query(Tweet).filter(Tweet.hashtag == self.name).delete()
        session.commit()
    
class   Crawler():
    '''
    Responsible of the skeleton of the crawler project
    self.conf: load configuration file
    api: authentication with the twitters API
    hashtag: dictionary of the hashtag scrapp by the project
    '''

    def __init__(self, path='crawler.json'):
        with open(path, 'r') as file:
            self.conf = json.load(file)
        auth = tweepy.OAuthHandler(self.conf['CONSUMER_KEY'], self.conf['CONSUMER_SECRET'])
        auth.set_access_token(self.conf['ACCESS_TOKEN'], self.conf['ACCESS_SECRET'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.hashtag = {}

    '''
    Link the programm with the database and fill in the scheme use
    '''
    def linkDB(self):
        engine = create_engine(self.conf['DB_ACCESS'])
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    '''
    Record a new hashtag (with a new research on twitters api)
    if the previous one is not older than 'DEADLINEREQUEST' in config file.
    '''
    def addHashtag(self, hashtag, session, api, deadlineRequest):
        if hashtag.name in self.hashtag:
            result = self.hashtag[hashtag.name]
            diff = datetime.now() - result.date
            print("DEBUG:ADDHASHTAG:divmod:", divmod(diff.days * 86400 + diff.seconds, 60))
            if divmod(diff.days * 86400 + diff.seconds, 60)[0] >= deadlineRequest:
                print("DEBUG:ADDHASHTAG:delete hashtag min:", divmod(diff.days * 86400 + diff.seconds, 60)[0])
                self.delHashtag(hashtag.name, session)
                self.hashtag[hashtag.name] = hashtag
                hashtag.sendQuery(api, session)
            else:
                print("DEBUG:ADDHASHTAG:nothing to do diff min:")   
        else:
            print("DEBUG:ADDHASHTAG:add hashtag")
            self.hashtag[hashtag.name] = hashtag
            hashtag.sendQuery(api, session)

    '''
    Delete one hashtag from the self.hashtag dictionary
    '''
    def delHashtag(self, hashtag, session):
        if hashtag in self.hashtag:
            self.hashtag[hashtag].erease(session)
            del self.hashtag[hashtag]

    '''
    Return one hashtag from self.hashtag dictionary
    '''
    def getHashtag(self, hashtagtitle, session):
        if hashtagtitle in self.hashtag:
            result = self.hashtag[hashtagtitle]
            return result
        return None

## Create db and table for (debug and SQLITE database)
crawler = Crawler()
engine = create_engine(crawler.conf['DB_ACCESS'])
Base.metadata.create_all(engine)
