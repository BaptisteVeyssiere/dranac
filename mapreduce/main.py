import json
from flask import Flask, jsonify

from mapreduce import mapreduce_pipeline
from src.tweet_input_reader import TweetInputReader
from src.database_output_writer import DatabaseOutputWriter
from src.mapreduce_jobs import CountTweetsPerHourPipeline, AverageWordsPipeline, UserNbrPipeline
from src.tweet import TweetManager
from src.request import RequestManager, Request
from src.api_output import APIOutput

app = Flask(__name__)

def getFavorites(tweets, number):
    """Sort the tweets by favorites to get tweets with the higher number of favorites"""

    tweets = sorted(tweets, key=lambda tweet: tweet.favorite, reverse=True)

    # Get only the first tweets of the sorted list
    tweets = tweets[:number]

    return json.dumps([tweet.__dict__ for tweet in tweets])


@app.route("/request/add/<session_id>/<hashtag>")
def add_request(session_id, hashtag):
    """Start a new request to mapreduce"""

    # Get tweets from the crawler
    json_content = TweetManager.getJson(hashtag)
    tweets = TweetManager.jsonToTweets(json_content)
    if (tweets is False) or (tweets is None) or hasattr(tweets, 'status'):
        return jsonify(status=False)

    # Start all the mapreduce pipelines
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

    # Create the request entry in the Datastore
    request_manager = RequestManager.addRequest(session_id, hashtag, pipelines, getFavorites(tweets, 3))

    return jsonify(status=True)


@app.route("/request/get/<session_id>/<hashtag>")
def get_request(session_id, hashtag):
    """Get the statistics about a certain hashtag"""

    # Get the pipelines related to the request
    pipelines = RequestManager.getRequestPipelines(session_id, hashtag)
    if pipelines is None:
        return jsonify(status=False)

    # Check each pipeline to check if its ended
    for pipeline_id in pipelines:
        pipeline = mapreduce_pipeline.MapreducePipeline.from_id(pipeline_id)
        if not pipeline.has_finalized:
            return jsonify(status=False)
    RequestManager.endRequest(session_id, hashtag)

    # Get the statistics and return it in JSON
    request = RequestManager.getRequest(session_id, hashtag)

    return jsonify(tweets_per_hour=APIOutput.sortDates(request.tweets_per_hour),
                   average_words=request.average_words,
                   user_nbr=request.user_nbr,
                   favorites=TweetManager.jsonToTweets(request.favorite))

# Start the API
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
