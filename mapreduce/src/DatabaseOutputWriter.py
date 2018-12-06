from mapreduce.output_writers import OutputWriter, _get_params
from mapreduce.errors import BadWriterParamsError
from mapreduce import context
from Request import Request, RequestManager

class DatabaseOutputWriter(OutputWriter):
    HASHTAG = "hashtag"
    SESSION_ID = "session_id"
    FIELD = "field"

    def __init__(self, hashtag, session_id, field):
        super(DatabaseOutputWriter, self).__init__()
        self._hashtag = hashtag
        self._session_id = session_id
        self._field = field

    @classmethod
    def create(cls, mr_spec, shard_number, shard_attempt, _writer_state=None):
        # Get params for the Output Writer
        params = _get_params(mr_spec.mapper)
        hashtag = params.get(cls.HASHTAG)
        session_id = params.get(cls.SESSION_ID)
        field = params.get(cls.FIELD)

        # Return parameters needed to create a new instance of the Output Writer
        return cls(hashtag, session_id, field)

    def write(self, data):
        ctx = context.get()
        db_pool = ctx.get_pool('database_pool')
        if not db_pool:
            db_pool = _DatabasePool(ctx=ctx, session_id=self._session_id, hashtag=self._hashtag, field=self._field)
            ctx.register_pool('database_pool', db_pool)

        db_pool.append(data)

    @classmethod
    def get_filenames(cls, mapreduce_state):
        return []

    @classmethod
    def validate(cls, mapper_spec):
        if mapper_spec.output_writer_class() != cls:
            raise BadWriterParamsError("Mapper output writer class mismatch")

        params = _get_params(mapper_spec)
        if cls.HASHTAG not in params:
            raise BadWriterParamsError("Must specify %s" % cls.HASHTAG)
        if not isinstance(str(params[cls.HASHTAG]), str):
            raise BadWriterParamsError("%s should be a string" % cls.HASHTAG)
        if cls.SESSION_ID not in params:
            raise BadWriterParamsError("Must specify %s" % cls.SESSION_ID)
        if not isinstance(str(params[cls.SESSION_ID]), str):
            raise BadWriterParamsError("%s should be a string" % cls.SESSION_ID)
        if cls.FIELD not in params:
            raise BadWriterParamsError("Must specify %s" % cls.FIELD)
        if not isinstance(str(params[cls.FIELD]), str):
            raise BadWriterParamsError("%s should be a string" % cls.FIELD)


    @classmethod
    def from_json(cls, state):
        return cls(state[cls.HASHTAG],
                   state[cls.SESSION_ID],
                   state[cls.FIELD])

    def to_json(self):
        return {self.HASHTAG: self._hashtag, self.SESSION_ID: self._session_id, self.FIELD: self._field}

    @classmethod
    def finalize(self, ctx, shard_state):
        return

class _DatabasePool(context.Pool):
    
    def __init__(self, ctx=None, session_id=None, hashtag=None, field=None):
        self._actions = []
        self._size = 0
        self._ctx = ctx
        self._session_id = session_id
        self._hashtag = hashtag
        self._field = field

    def append(self, action):
        self._actions.append(action)
        self._size += 1
        if self._size > 200:
            self.flush()

    def flush(self):
        if self._actions:
            for output in self._actions:
                RequestManager.setField(self._field, self._session_id, self._hashtag, output)
        self._actions = []
        self._size = 0
