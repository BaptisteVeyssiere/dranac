from flask import Flask, jsonify

# New dependencies

from mapreduce import mapreduce_pipeline
from src.DatabaseInputReader import DatabaseInputReader
from src.DatabaseOutputWriter import DatabaseOutputWriter
from src.mapreduce_jobs import CountTweetsPerHourPipeline
from src.Tweet import TweetManager, Tweet
from src.Request import RequestManager, Request

app = Flask(__name__)

@app.route("/request/add/<session_id>/<hashtag>")
def add_request(session_id, hashtag):
    pipelines = []
    pipeline = CountTweetsPerHourPipeline(session_id, hashtag)
    pipeline.start()
    pipelines.append(pipeline.pipeline_id)
    # pipeline = AverageWordsPipeline(session_id, hashtag)
    # pipeline.start()
    # pipelines.append(pipeline.pipeline_id)
    # pipeline = UserNbrPipeline(session_id, hashtag)
    # pipeline.start()
    # pipelines.append(pipeline.pipeline_id)
    request_manager = RequestManager.addRequest(session_id, hashtag, pipelines)
    return 'OK'

@app.route("/request/get/<session_id>/<hashtag>")
def get_request(session_id, hashtag):
    pipelines = RequestManager.getRequestPipelines(session_id, hashtag)
    for pipeline_id in pipelines:
        pipeline = mapreduce_pipeline.MapreducePipeline.from_id(pipeline_id)
        if not pipeline.has_finalized:
            return ""
    RequestManager.endRequest(session_id, hashtag)
    request = RequestManager.getRequest(session_id, hashtag)
    return jsonify(tweets_per_hour=request.tweets_per_hour,
                   average_words=request.average_words,
                   user_nbr=request.user_nbr)

# Delete /db route before deploying

@app.route("/db")
def db():
    tweet = Tweet(hashtag='#trump',
                  user='macron',
                  date='Fri Nov 30 02:04:08 +0000 2018',
                  content="I am better than Trump",
                  favorite=1000000000)
    tweet.put()
    tweet = Tweet(hashtag='#macron',
                  user='trump',
                  date='Fri Nov 30 02:04:08 +0000 2018',
                  content="I am better than Macron",
                  favorite=1000000000)
    tweet.put()
    return 'tweets added'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
