from bson import ObjectId
from pymongo import MongoClient
import requests
from lxml import etree
from flask import Flask, render_template, jsonify, request, render_template_string
from flask.json.provider import JSONProvider
from pprint import pprint
import json
import sys

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungle

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

app.json = CustomJSONProvider(app)


@app.route("/")
def head():
    print(list(db.movies.find({'trashed': '1'}, {}).sort('like', -1)))
    return render_template("index.html", number1 = 12, number2 = 34)

@app.route("/about")
def second():
    return render_template("about.html", hazirlayan = "Feyzullah SARI")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug = True)