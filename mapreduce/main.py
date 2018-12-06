import json
from flask import Flask, jsonify

# New dependencies

from mapreduce import mapreduce_pipeline
from src.TweetInputReader import TweetInputReader
from src.DatabaseOutputWriter import DatabaseOutputWriter
from src.mapreduce_jobs import CountTweetsPerHourPipeline, AverageWordsPipeline, UserNbrPipeline
from src.Tweet import TweetManager
from src.Request import RequestManager, Request
from src.APIOutput import APIOutput

app = Flask(__name__)

def getFavorites(tweets, number):
    tweets = sorted(tweets, key=lambda tweet: tweet.favorite, reverse=True)
    tweets = tweets[:number]
    return json.dumps([tweet.__dict__ for tweet in tweets])

@app.route("/request/add/<session_id>/<hashtag>")
def add_request(session_id, hashtag):
    json_content = TweetManager.getJson(hashtag)
    tweets = TweetManager.jsonToTweets(json_content)
    if (tweets is False) or (tweets is None) or hasattr(tweets, 'status'):
        return jsonify(status=False)
    getFavorites(tweets, 3)
    pipelines = []
    pipeline = CountTweetsPerHourPipeline(session_id, hashtag, json_content)
    pipeline.start()
    pipelines.append(pipeline.pipeline_id)
    pipeline = AverageWordsPipeline(session_id, hashtag, json_content)
    pipeline.start()
    pipelines.append(pipeline.pipeline_id)
    pipeline = UserNbrPipeline(session_id, hashtag, json_content)
    pipeline.start()
    pipelines.append(pipeline.pipeline_id)
    request_manager = RequestManager.addRequest(session_id, hashtag, pipelines, getFavorites(tweets, 3))
    return jsonify(status=True)

@app.route("/request/get/<session_id>/<hashtag>")
def get_request(session_id, hashtag):
    pipelines = RequestManager.getRequestPipelines(session_id, hashtag)
    if pipelines is None:
        return jsonify(status=False)
    for pipeline_id in pipelines:
        pipeline = mapreduce_pipeline.MapreducePipeline.from_id(pipeline_id)
        if not pipeline.has_finalized:
            return jsonify(status=False)
    RequestManager.endRequest(session_id, hashtag)
    request = RequestManager.getRequest(session_id, hashtag)
    return jsonify(tweets_per_hour=APIOutput.sortDates(request.tweets_per_hour),
                   average_words=request.average_words,
                   user_nbr=request.user_nbr,
                   favorites=TweetManager.jsonToTweets(request.favorite))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
