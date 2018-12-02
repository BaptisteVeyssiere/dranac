import collections
from datetime import datetime
from dateutil import parser
from google.appengine.api import app_identity
from mapreduce import mapreduce_pipeline, base_handler

def tweets_per_hour_map(tweet):
    print tweet.date
    date = parser.parse(tweet.date)
    yield (date.strftime('%d/%m/%Y %H'), 1)

def tweets_per_hour_reduce(key, values):
    yield "%s: %d" % (key, sum([int(i) for i in values]))

class CountTweetsPerHourPipeline(base_handler.PipelineBase):

    def run(self, session_id, hashtag):
        mapper_params = {
            "hashtag": hashtag,
        }
        reducer_params = {
            "output_writer": {
                "hashtag": hashtag,
                "session_id": session_id,
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

