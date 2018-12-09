import datetime
import json
from google.appengine.ext import db

# Define Request object in Datastore
class Request(db.Model):
    session_id = db.StringProperty()
    hashtag = db.StringProperty()
    pipelines = db.StringProperty()
    timestamp = db.DateProperty()
    finished = db.BooleanProperty()
    tweets_per_hour = db.TextProperty()
    average_words = db.IntegerProperty()
    user_nbr = db.IntegerProperty()
    favorite = db.TextProperty()

class RequestManager():

    @classmethod
    def getRequest(self, session_id, hashtag):
        """Get the Request entry linked with the right session_id and hashtag"""

        query = Request.all()
        query.filter("session_id =", session_id)
        query.filter("hashtag =", hashtag)
        result = query.get()
        return result
        
    @classmethod
    def addRequest(self, session_id, hashtag, pipelines, favorites):
        """Add a new Request to the Datastore"""

        result = self.getRequest(session_id, hashtag)
        if result:
            result.delete()
        request = Request(session_id=session_id,
                          hashtag=hashtag,
                          pipelines=','.join(pipelines),
                          timestamp=datetime.datetime.now().date(),
                          favorite=favorites,
                          finished=False)
        request.put()

    @classmethod
    def getRequestPipelines(self, session_id, hashtag):
        """Get the pipelines used in a certain Request"""

        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        pipelines = result.pipelines.split(',')
        return pipelines

    @classmethod
    def endRequest(self, session_id, hashtag):
        """Set the Request to ended"""

        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        result.finished = True
        result.put()

    @classmethod
    def addTweetsPerHour(self, session_id, hashtag, pipeline_result):
        """Set the tweets_per_hour field of a Request in the Datastore"""

        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        current = []

         # Get the result already present to concatenate it with the new content
        if result.tweets_per_hour:
            current = json.loads(result.tweets_per_hour)
        for elem in pipeline_result:
            current.append(elem)
        result.tweets_per_hour = json.dumps(current)
        result.put()

    @classmethod
    def addUserNbr(self, session_id, hashtag, pipeline_result):
        """Set the user_nbr field of a Request in the Datastore"""

        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        print pipeline_result
        result.user_nbr = pipeline_result[0]
        result.put()

    @classmethod
    def addAverageWords(self, session_id, hashtag, pipeline_result):
        """Set the average_words field of a Request in the Datastore"""

        result = self.getRequest(session_id, hashtag)
        if not result:
            return
        result.average_words = pipeline_result[0]
        result.put()

    @classmethod
    def setField(self, field, session_id, hashtag, pipeline_result):
        """Use to choose which field of a Request to update in the Datastore"""

        switch = {'tweets_per_hour':self.addTweetsPerHour,
                  'user_nbr':self.addUserNbr,
                  'average_words':self.addAverageWords}
        switch[field](session_id, hashtag, pipeline_result)


