import datetime
import json
from google.appengine.ext import db

class Request(db.Model):
    session_id = db.StringProperty()
    hashtag = db.StringProperty()
    pipelines = db.StringProperty()
    timestamp = db.DateProperty()
    finished = db.BooleanProperty()
    tweets_per_hour = db.TextProperty()
    average_words = db.IntegerProperty()
    user_nbr = db.IntegerProperty()

class RequestManager():

    @classmethod
    def getRequest(self, session_id, hashtag):
        query = Request.all()
        query.filter("session_id =", session_id)
        query.filter("hashtag =", hashtag)
        result = query.get()
        return result
        
    @classmethod
    def addRequest(self, session_id, hashtag, pipelines):
        result = self.getRequest(session_id, hashtag)
        if result:
            result.delete()
        request = Request(session_id=session_id,
                          hashtag=hashtag,
                          pipelines=','.join(pipelines),
                          timestamp=datetime.datetime.now().date(),
                          finished=False)
        request.put()

    @classmethod
    def getRequestPipelines(self, session_id, hashtag):
        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        pipelines = result.pipelines.split(',')
        return pipelines

    @classmethod
    def endRequest(self, session_id, hashtag):
        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        result.finished = True
        result.put()

    @classmethod
    def addTweetsPerHour(self, session_id, hashtag, pipeline_result):
        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        current = []
        if result.tweets_per_hour:
            current = json.loads(result.tweets_per_hour)
        current.append(pipeline_result)
        result.tweets_per_hour = json.dumps(current)
        result.put()

    @classmethod
    def addUserNbr(self, session_id, hashtag, pipeline_result):
        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        result.user_nbr = pipeline_result
        result.put()

    @classmethod
    def addAverageWords(self, session_id, hashtag, pipeline_result):
        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        result.average_words = pipeline_result
        result.put()

    @classmethod
    def setField(self, field, session_id, hashtag, pipeline_result):
        switch = {'tweets_per_hour':self.addTweetsPerHour,
                  'user_nbr':self.addUserNbr,
                  'average_words':self.addAverageWords}
        switch[field](session_id, hashtag, pipeline_result)


