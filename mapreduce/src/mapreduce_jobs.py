import collections
from datetime import datetime
from dateutil import parser
from google.appengine.api import app_identity
from mapreduce import mapreduce_pipeline, base_handler

def tweets_per_hour_map(tweet):
    date = parser.parse(tweet.date)
    yield (date.strftime('%d/%m/%Y %H'), 1)

def average_words_map(tweet):
    word_nbr = len(tweet.content.split())
    yield (1, word_nbr)

def user_nbr_map(tweet):
    yield (1, tweet.user)

def tweets_per_hour_reduce(key, values):
    yield "%s: %d" % (key, sum([int(i) for i in values]))

def average_words_reduce(key, values):
    yield (sum([int(i) for i in values]) / len(values))

def user_nbr_reduce(key, values):
    yield len(set(values))

class CountTweetsPerHourPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag):
        mapper_params = {
            "hashtag": hashtag,
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
            "main.DatabaseInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=2)

class AverageWordsPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag):
        mapper_params = {
            "hashtag": hashtag,
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
            "main.DatabaseInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=2)

class UserNbrPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag):
        mapper_params = {
            "hashtag": hashtag,
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
            "main.DatabaseInputReader",
            "main.DatabaseOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=2)

