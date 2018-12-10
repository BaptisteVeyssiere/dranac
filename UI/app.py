from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import jsonify
from time import sleep
import requests
import re
import json

app = Flask(__name__)

APP_NAME = "Dranac"

# Error messages
ERROR_INVALID = "Error: Invalid hashtag."
ERROR_SERVER = "Error: Internal error. Please try again."
ERROR_TWEET = "An error occurred with this tweet."

# Crawler service URLs
CRAWLER_URL = "https://crawler-dot-corded-smithy-222417.appspot.com/v1.0/hashtag"

# Mapreduce service URLs
MAPREDUCE_URL = "https://mapreduce-dot-corded-smithy-222417.appspot.com/"
MAPREDUCE_ADD = "request/add/1/"
MAPREDUCE_GET = "request/get/1/"


@app.route('/start_stats', methods=['POST'])
def start_stats():
    """
    Check the given hashtag, start the Mapreduce service with it and give back a status
    True in json if everything is working as expected or an error message if there was
    an error.

    :return: A json containing status True or an html content with an error message
    """
    hashtag = request.form.get('ht')
    if hashtag is None or not check_hashtag(hashtag):
        return make_response(render_template("error.html", message=ERROR_INVALID))
    status = False
    while not status:
        response = requests.get(MAPREDUCE_URL + MAPREDUCE_ADD + hashtag)
        if response.status_code != 200 or response.headers['content-type'].find('application/json') < 0:
            return make_response(render_template("error.html", message=ERROR_SERVER))
        content = json.loads(response.content)
        status = content.get('status')
        if status is None:
            return make_response(render_template("error.html", message=ERROR_SERVER))
        sleep(0.5)
    return jsonify({'status': True})


def get_embedded_tweet(url, fallback_value):
    """
    Make a request to the public Twitter API to get embedded tweets from the given url

    :param url: The URL where to make the request
    :param fallback_value: The value to use in case of an unavailable embedded tweet
    :return: The embedded tweet, the fallback tweet or an error.
    """
    response = requests.get(url)
    if response.status_code != 200 or response.headers['content-type'].find("application/json") < 0:
        if fallback_value is not None:
            return fallback_value
        return ERROR_TWEET
    content = json.loads(response.content)
    if content.get('html') is not None:
        return content.get('html')
    if fallback_value is not None:
        return fallback_value
    return ERROR_TWEET


def get_favorites(favorite_list):
    """
    Try to get a beautiful tweet of the favourite ones as embedded tweets or
    use the content of the tweet not formatted as a last resort

    :param favorite_list: The list of favourite tweet
    :return: A list of favorite tweet reformatted
    """
    favorites = []
    if favorite_list is not None:
        for fav in favorite_list:
            if fav.get('embeddedTweet') is not None:
                favorites.append({'tweet': True,
                                  'content': get_embedded_tweet(fav['embeddedTweet'],
                                                                fav.get('content'))})
            elif fav.get('content') is not None:
                favorites.append({'tweet': True, 'content': fav['content']})
            else:
                favorites = [{'tweet': False,
                              'content': 'Favorite tweets is not implemented yet.'}]
                break
    if len(favorites) < 1:
        favorites = [{'tweet': False,
                      'content': 'There is no favorite tweet.'}]
    return favorites


def get_graph_data(tweets_per_hour):
    """
    Format the required data in order to make a chart with them in JavaScript

    :param tweets_per_hour: A list of number of tweets for a given date and hour
    :return: The formated data for chart.js
    """
    tweets_per_hour = [s.encode('utf-8') for s in tweets_per_hour]
    time_list = [i.decode('utf-8').split(':', 1)[0].replace(" ", "/") for i in tweets_per_hour]
    nbr_list = [i.decode('utf-8').split(': ', 1)[1] for i in tweets_per_hour]
    data = []
    for i in range(len(time_list)):
        data.append({'x': time_list[i].split('/'), 'y': nbr_list[i]})
    return data


@app.route('/get_stats', methods=['POST'])
def get_stats():
    """
    Check the given hashtag, get the Mapreduce service's result of this hashtag and
    give back a status False in json if the result is not ready, an error message if there
    was an error or a html content generated with the result data of the Mapreduce job.

    :return: A json containing status False or an html content with an error message or with
    the resulting data
    """
    hashtag = request.form.get('ht')
    if hashtag is None or not check_hashtag(hashtag):
        return make_response(render_template("error.html", message=ERROR_INVALID))
    response = requests.get(MAPREDUCE_URL + MAPREDUCE_GET + hashtag)
    if response.status_code != 200 or response.headers['content-type'].find('application/json') < 0:
        return make_response(render_template("error.html", message=ERROR_SERVER))
    content = json.loads(response.content)
    if content.get('status') is not None and not content['status']:
        return jsonify({'status': False})
    try:
        data = get_graph_data(content['tweets_per_hour'])
        average_word = content['average_words']
        user_nbr = content['user_nbr']
        favorites = get_favorites(content.get('favorites'))
    except TypeError:
        return make_response(render_template("error.html", message=ERROR_SERVER))
    return make_response(render_template("hashtag_stats.html", data=data,
                                         user_nbr=user_nbr, average_word=average_word,
                                         favorites=favorites))


def check_hashtag(hashtag):
    """
    Check if the hashtag is correct

    :param hashtag: A string containing the hashtag
    :return: False if the hashtag is incorrect, otherwise True
    """
    if not isinstance(hashtag, str) or not hashtag:
        return False
    if re.fullmatch(r"(#|)(\w*[0-9a-zA-Z]+\w*[0-9a-zA-Z])", hashtag) is None:
        return False
    return True


def start_search_hashtag(hashtag):
    """
    Make a request to the Crawler service to start processing the given hashtag

    :param hashtag: The hashtag to be sent to the Crawler service
    :return: False if there is an error, otherwise True
    """
    data = {'hashtag': hashtag, 'lang': 'en'}
    response = requests.post(CRAWLER_URL, json=data)
    if response.status_code != 200:
        return False
    return True


@app.route('/search')
def search():
    """
    Check the given hashtag, start the Crawler service with it and give back a waiting page
    or an error message if there was an error.

    :return: The waiting html page if everything is alright, otherwise an error html page
    """
    hashtag = request.args.get('ht')
    if hashtag is None or not check_hashtag(hashtag):
        return make_response(render_template("search.html", title=APP_NAME,
                                             file="error.html", message=ERROR_INVALID))
    if hashtag[0] == "#":
        hashtag = hashtag[1:]
    if not start_search_hashtag(hashtag):
        return make_response(render_template("search.html", title=APP_NAME,
                                             file="error.html", message=ERROR_SERVER))
    return make_response(render_template("search.html", title=APP_NAME,
                                         file="loading.html", hashtag=hashtag))


@app.route('/')
def home():
    """
    Return the home page of Dranac

    :return: The html home page
    """
    return render_template("home.html", title=APP_NAME)


if __name__ == '__main__':
    app.run()
