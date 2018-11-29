import collections

from flask import Flask, make_response

from google.appengine.ext import blobstore

from google.appengine.api import app_identity

from mapreduce import mapreduce_pipeline
from mapreduce import base_handler

app = Flask(__name__)

def character_count_map(random_string):
    print random_string
    print 'A' * 100
    counter = collections.Counter(random_string)
    for character in counter.elements():
        yield (character, counter[character])

def character_count_reduce(key, values):
    yield "%s: %d\n" % (key, sum([int(i) for i in values]))

class CountCharactersPipeline(base_handler.PipelineBase):

    def run(self):
        bucket_name = app_identity.get_default_gcs_bucket_name()
        mapper_params = {
            "count": 1,
            "string_length": 5,
        }
        reducer_params = {
            "output_writer": {
                "bucket_name": bucket_name,
                "content_type": "text/plain",
            }
        }
        output = yield mapreduce_pipeline.MapreducePipeline(
            "character_count",
            "main.character_count_map",
            "main.character_count_reduce",
            "mapreduce.input_readers.RandomStringInputReader",
            "mapreduce.output_writers.GoogleCloudStorageOutputWriter",
            mapper_params=mapper_params,
            reducer_params=reducer_params,
            shards=1)

@app.route('/')
def home():
    pipeline = CountCharactersPipeline()
    pipeline.start()
    return "Hello world!"

@app.route("/result/<bkey>")
def result(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
