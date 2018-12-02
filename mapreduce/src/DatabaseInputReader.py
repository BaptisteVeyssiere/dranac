import os

from mapreduce.input_readers import InputReader, _get_params
from mapreduce.errors import BadReaderParamsError
from mapreduce import context, base_handler

from Tweet import Tweet, TweetManager

class DatabaseInputReader(InputReader):
    COUNT = "count"
    START = "start"
    HASHTAG = "hashtag"

    def __init__(self, count, start, hashtag):
        self._count = count
        self._start = start
        self._hashtag = hashtag

    @classmethod
    def split_input(cls, mapper_spec):
        # Get Input Reader parameters
        params = _get_params(mapper_spec)
        hashtag = params[cls.HASHTAG]

        # Get number of lines processed by each shard
        shard_count = mapper_spec.shard_count
        tweet_nbr = sum(1 for elem in TweetManager.getTweets(hashtag))
        tweet_per_shard = tweet_nbr // shard_count

        # Create the list of input readers
        mr_input_readers = [cls(tweet_per_shard, i*tweet_per_shard, hashtag) for i in range(shard_count)]

        # Check if there are lines not assigned to a shard, and create another input reader if so
        left = tweet_nbr - tweet_per_shard*shard_count
        if left > 0:
            mr_input_readers.append(cls(left, tweet_per_shard*shard_count, hashtag))

        return mr_input_readers

    def __iter__(self):
        tweets = TweetManager.getTweets(self._hashtag)
        i = 0
        for tweet in tweets:
            # Skip elems until the start of its portion
            if i < self._start:
                continue
            i += 1
            if self._count <= 0:
                break
            self._count -= 1
            yield tweet

    @classmethod
    def from_json(cls, input_shard_state):
        return cls(input_shard_state[cls.COUNT],
                   input_shard_state[cls.START],
                   input_shard_state[cls.HASHTAG])

    def to_json(self):
        return {self.COUNT: self._count, self.START: self._start, self.HASHTAG: self._hashtag}

    @classmethod
    def validate(cls, mapper_spec):
        if mapper_spec.input_reader_class() != cls:
            raise BadReaderParamsError("Mapper input reader class mismatch")

        params = _get_params(mapper_spec)
        if cls.HASHTAG not in params:
            raise BadReaderParamsError("Must specify %s" % cls.HASHTAG)
        if not isinstance(str(params[cls.HASHTAG]), str):
            raise BadReaderParamsError("%s should be a string")
