import collections
import os

from flask import Flask, make_response

from google.appengine.ext import blobstore

from google.appengine.api import app_identity

from mapreduce.input_readers import InputReader, _get_params as input_readers_get_params
from mapreduce.output_writers import OutputWriter, _get_params as output_writers_get_params
from mapreduce.errors import BadReaderParamsError
from mapreduce import mapreduce_pipeline
from mapreduce import base_handler
from mapreduce import context

app = Flask(__name__)

class DatabaseOutputWriter(OutputWriter):

    def __init__(self):
        super(DatabaseOutputWriter, self).__init__()

    @classmethod
    def create(cls, mr_spec, shard_number, shard_attempt, _writer_state=None):
        # Get params for the Output Writer
        params = output_writers_get_params(mr_spec)

        # Return parameters needed to create a new instance of the Output Writer
        return cls()

    def write(self, data):
        ctx = context.get()
        db_pool = ctx.get_pool('database_pool')
        if not db_pool:
            db_pool = _DatabasePool(ctx=ctx)
            ctx.register_pool('database_pool', db_pool)

        db_pool.append(data)

    @classmethod
    def get_filenames(cls, mapreduce_state):
        return []

    @classmethod
    def validate(cls, mapper_spec):
        if mapper_spec.output_writer_class() != cls:
            raise BadWriterParamsError("Mapper output writer class mismatch")

        params = input_readers_get_params(mapper_spec)

    @classmethod
    def from_json(cls, state):
        return cls()

    def to_json(self):
        return {}

    @classmethod
    def finalize(self, ctx, shard_state):
        print "Finalize"

class _DatabasePool(context.Pool):
    
    def __init__(self, ctx=None):
        self._actions = []
        self._size = 0
        self._ctx = ctx

    def append(self, action):
        self._actions.append(action)
        self._size += 1
        if self._size > 200:
            self.flush()

    def flush(self):
        if self._actions:
            for output in self._actions:
                print output
        self._actions = []
        self._size = 0

class TweetInputReader(InputReader):

    FILENAME = "filename"
    COUNT = "count"
    START = "start"

    def __init__(self, count, start, filename):
        self._count = count
        self._start = start
        self._filename = filename

    @classmethod
    def split_input(cls, mapper_spec):
        # Get Input Reader parameters
        params = input_readers_get_params(mapper_spec)
        filename = params[cls.FILENAME]
        
        # Get number of lines processed by each shard
        shard_count = mapper_spec.shard_count
        line_nbr = sum(1 for line in open(filename))
        line_per_shard = line_nbr // shard_count
        
        # Create the list of input readers
        mr_input_readers = [cls(line_per_shard, i*line_per_shard, filename) for i in range(shard_count)]
        
        # Check if there are lines not assigned to a shard, and create another input reader if so
        left = line_nbr - line_per_shard*shard_count
        if left > 0:
            mr_input_readers.append(cls(left, line_per_shard*shard_count, filename))
        
        return mr_input_readers

    def __iter__(self):
        with open(self._filename) as f:
            for i in xrange(self._start):
                f.next()
            for line in f:
                if self._count <= 0:
                    break
                self._count -= 1
                yield line

    @classmethod
    def from_json(cls, input_shard_state):
        return cls(input_shard_state[cls.COUNT],
                   input_shard_state[cls.START],
                   input_shard_state[cls.FILENAME])

    def to_json(self):
        return {self.COUNT: self._count, self.START: self._start, self.FILENAME: self._filename}

    @classmethod
    def validate(cls, mapper_spec):
        if mapper_spec.input_reader_class() != cls:
            raise BadReaderParamsError("Mapper input reader class mismatch")

        params = input_readers_get_params(mapper_spec)
        if cls.FILENAME not in params:
            raise BadReaderParamsError("Must specify %s" % cls.FILENAME)
        if not isinstance(str(params[cls.FILENAME]), str):
            raise BadReaderParamsError("%s should be a string")
        if not os.path.isfile('./' + params[cls.FILENAME]):
            raise BadReaderParamsError("file " + params[cls.FILENAME] + " does not exist")

def character_count_map(random_string):
    print random_string
    counter = collections.Counter(random_string)
    for character in counter.elements():
        yield (character, 1)

def character_count_reduce(key, values):
    yield "%s: %d\n" % (key, sum([int(i) for i in values]))

class CountCharactersPipeline(base_handler.PipelineBase):

    def run(self):
        bucket_name = app_identity.get_default_gcs_bucket_name()
        mapper_params = {
            "filename": "test.txt",
        }
        '''
        reducer_params = {
            "output_writer": {
                "bucket_name": bucket_name,
                "content_type": "text/plain",
            }
        }
        '''
        reducer_params = {}
        output = yield mapreduce_pipeline.MapreducePipeline(
            "character_count",
            "main.character_count_map",
            "main.character_count_reduce",
            "main.TweetInputReader",
            "main.DatabaseOutputWriter",
            #"mapreduce.output_writers.GoogleCloudStorageOutputWriter",
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
