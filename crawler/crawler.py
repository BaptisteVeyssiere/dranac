#!/usr/bin/env python3

from flask import Flask, jsonify, abort, request
import json

from twython import Twython
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from entities import Base, Tweet, Hashtag, Crawler

app = Flask(__name__)

crawler = Crawler()
crawler.linkDB()

@app.route('/', methods=['GET'])
def get_home():
    return jsonify({'route': ['/v1.0/hashtag --> POST', '/v1.0/:hashtag --> get', '/v1.0/debug --> get']})

@app.route('/v1.0/hashtag', methods=['POST'])
def post_launchProcess():
    if not request.json or not 'hashtag' in request.json :
        abort(400)
    hashtag = Hashtag('#' + request.json['hashtag'], request.json['lang'])
    hashtag.createQuery()
    hashtag.sendQuery(crawler.python_tweets, crawler.session)
    crawler.addHashtag(hashtag)
    return jsonify({'hashtag': hashtag.name})

@app.route('/v1.0/<string:hashtag>', methods=['GET'])
def get_processResult(hashtag):
    h = crawler.getHashtag('#' + hashtag, crawler.session)
    if h != None:
        return jsonify(h.getTweetsList(crawler.session))
    return jsonify({'status': 'cannot find #' + hashtag})

@app.route('/v1.0/debug/<string:hashtag>', methods=['GET'])
def api_debug(hashtag):
    result = crawler.session.query(Tweet).filter(Tweet.hashtag == hashtag).all()
    return jsonify([{'user':elem.user, 'date':elem.date, 'content':elem.content, 'favorite':elem.favorite} for elem in result])
    
if __name__ == '__main__':
    app.run(debug=True)

## TODO changer les status request ex 200, 400, 404, ...
