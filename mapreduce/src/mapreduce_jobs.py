import collections
from datetime import datetime
from dateutil import parser
from google.appengine.api import app_identity
from mapreduce import mapreduce_pipeline, base_handler

def tweets_per_hour_map(tweet):
    """Map function for the tweets_per_hour pipeline"""

    date = parser.parse(tweet.date)
    yield (date.strftime('%d/%m/%Y %H'), 1)

def average_words_map(tweet):
    """Map function for the average_words pipeline"""

    word_nbr = len(tweet.content.split())
    yield (1, word_nbr)

def user_nbr_map(tweet):
    """Map function for the user_nbr pipeline"""

    yield (1, tweet.user)

def tweets_per_hour_reduce(key, values):
    """Reduce function for the tweets_per_hour pipeline"""

    yield "%s: %d" % (key, sum([int(i) for i in values]))

def average_words_reduce(key, values):
    """Reduce function for the average_words pipeline"""

    yield (sum([int(i) for i in values]) / len(values))

def user_nbr_reduce(key, values):
    """Reduce function for the user_nbr pipeline"""

    yield len(set(values))

class CountTweetsPerHourPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag, tweets):
        """Method called to run the pipeline and define the parameters"""

        mapper_params = {
            "hashtag": hashtag,
            "tweets": tweets,
        }
        reducer_params = {
            "output_writer": {
                "hashtag": hashtag,
                "session_id": session_id,
                "field": "tweets_per_hour",
            }
        }
        output = yield mapreduce_pipeline.MapreducePipeline(
            "tweets_per_hour",
            "src.mapreduce_jobs.tweets_per_hour_map",
            "src.mapreduce_jobs.tweets_per_hour_reduce",
            "main.TweetInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=1)

class AverageWordsPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag, tweets):
        """Method called to run the pipeline and define the parameters"""

        mapper_params = {
            "hashtag": hashtag,
            "tweets": tweets,
        }
        reducer_params = {
            "output_writer": {
                "hashtag": hashtag,
                "session_id": session_id,
                "field": "average_words",
            }
        }
        output = yield mapreduce_pipeline.MapreducePipeline(
            "average_words",
            "src.mapreduce_jobs.average_words_map",
            "src.mapreduce_jobs.average_words_reduce",
            "main.TweetInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=1)

class UserNbrPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag, tweets):
        """Method called to run the pipeline and define the parameters"""

        mapper_params = {
            "hashtag": hashtag,
            "tweets": tweets,
        }
        reducer_params = {
            "output_writer": {
                "hashtag": hashtag,
                "session_id": session_id,
                "field": "user_nbr",
            }
        }
        output = yield mapreduce_pipeline.MapreducePipeline(
            "user_nbr",
            "src.mapreduce_jobs.user_nbr_map",
            "src.mapreduce_jobs.user_nbr_reduce",
            "main.TweetInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=1)

