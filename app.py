from bson import ObjectId
from pymongo import MongoClient
import requests
from lxml import etree
from flask import Flask, render_template, jsonify, request, render_template_string
from flask.json.provider import JSONProvider
from pprint import pprint
import json
import sys

from app_instance import app
import login
from mongo_setup import get_db
db = get_db()

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
    # print(list(db.movies.find({'trashed': '1'}, {}).sort('like', -1)))
    return render_template("index.html", number1 = 12, number2 = 34)

@app.route("/about")
def second():
    return render_template("about.html", hazirlayan = "Feyzullah SARI")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug = True)


@app.route("/main")
def main():
    if chek_token():
        return render_template("main.html")
    return redirect("/login")
    
def chek_token():
    #클라이언트에게서 토큰 가져오기 
    token = request.cookies.get('Authorization')
    
    #토큰이 없다면 거짓반환
    if(not token) : return False
    
    #토큰 디코딩을 위해 'Bearer%20' 제거 후 디코딩
    token = token.replace('Bearer%20', '').strip()
    cur_user = decode_token(token)
    
    #토큰에 저장된 유저이름이 DB에서 찾아진다면 참 반환
    if (db.user.find_one({'user_id' : cur_user['sub']})):
        #if(check_token_fresh(user)):
        return True
    return False

#로그아웃
@app.route("/logout", methods=['POST'])
def log_out():
    # 제거할 토큰의 값을 가져온다
    token = request.cookies.get('Authorization')
    # 제거할 토큰의 값을 보낸다
    return jsonify({'result': 'success', 'access_token' : token})
