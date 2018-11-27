#!/usr/bin/env python3

import json
from twython import Twython
import pandas as pd

def saveConf(conf):
    with open('wrapperconf.json', 'w') as file:
        json.dump(conf, file, indent=4)

def loadConf(path):
    with open(path, 'r') as file:
        conf = json.load(file)
    return conf

def CreateQuery(keyword, resulType, count, lang='en'):
    query = {
        'q': keyword,
        'result_type': resulType,
        'count': count,
        'lang': lang,
    }
    return query
    
def SendQuery(query):
    dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
    for status in python_tweets.search(**query)['statuses']:
        dict_['user'].append(status['user']['screen_name'])
        dict_['date'].append(status['created_at'])
        dict_['text'].append(status['text'])
        dict_['favorite_count'].append(status['favorite_count'])

    return dict_
        
conf = loadConf('wrapperconf.json')
print(json.dumps(conf, indent=4))

# Instantiate object
python_tweets = Twython(conf['CONSUMER_KEY'], conf['CONSUMER_SECRET'])

# Create and send query to twitter
query = CreateQuery('#trump', 'popular', 10, 'fr')
result = SendQuery(query)

# Sort data from the query
df = pd.DataFrame(result)
df.sort_values(by='favorite_count', inplace=True, ascending=False)
print(json.dumps(result, indent=4))
