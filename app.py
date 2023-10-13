from bson import ObjectId
from pymongo import MongoClient
import requests
from lxml import etree
from flask import Flask, render_template, jsonify, request, render_template_string, redirect
from flask.json.provider import JSONProvider
from pprint import pprint
import json
import sys
from datetime import datetime

from app_instance import *
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
    return redirect('/login')

@app.route("/about")
def second():
    return render_template("about.html", hazirlayan = "Feyzullah SARI")


@app.route("/main")
def main():
    user_id = None
    if  user := chek_token() :
        users = list(db.user.find())
        print('ggg' , user)
        return render_template("main.html", user_list=users , user=user)
    return redirect("/login")
    
def chek_token():
    #클라이언트에게서 토큰 가져오기 
    token = request.cookies.get('Authorization')
    
    #토큰이 없다면 거짓반환
    if(not token) : return False
    
    #토큰 디코딩을 위해 'Bearer%20' 제거 후 디코딩
    token = token.replace('Bearer%20', '').strip()
    cur_user = decode_token(token)
    user = None
    #토큰에 저장된 유저이름이 DB에서 찾아진다면 참 반환
    if (user:= db.user.find_one({'user_id' : cur_user['sub']})):
        #if(check_token_fresh(user)):
        return user
    return False



# API 1 : 포스트 목록 보여주기
@app.route('/api/list', methods=['GET'])
def show_post():
    today_date = request.args.get('searchdate',datetime.today().strftime("%Y-%m-%d"))
    search_user = request.args.get('searchuser','모두')
#     today_date = '2023-10-11'
#     print('today_date=', today_date)
    if search_user == '모두':
        posts = list(db.userpost.find({'post_date':today_date}))
    else:
        posts = list(db.userpost.find({'post_date':today_date,'user_id':search_user}))
#     for r in posts:
#          print(r)

    post_url = [ p['post_url'] for p in posts]

    pipeline = [
        {"$match": {"post_url": {"$in": post_url}}},  # Filtering by post_url using $in operator
        {"$group": {
            "_id": "$post_url",
            "count": {"$sum": 1},
            "data": {"$first": "$$ROOT"}  # $$ROOT refers to the entire document
        }},
        {"$replaceRoot": {  # Replaces the root with a merged version of the original document and the count
            "newRoot": {
                "$mergeObjects": ["$data", {"cnt": "$count"}]
            } 
        }}
    ]   

    postfight = list(db.postfight.aggregate(pipeline))
    postfight = { p['post_url'] : p['cnt']  for p in postfight}

    print('11',postfight)

    # SELECT *, count(*) as cnt FROM postfight WHERE post_date = '{$today_date}' GROUP BY post_url
    return jsonify({'result': 'success', 'post_list': posts , 'fight' : postfight})
    

# API 2 : 회원목록 보여주기
@app.route('/api/list/user', methods=['GET'])
def show_user():

    users = list(db.user.find({}))
#     for r in users:
#          print(r)

    return jsonify({'result': 'success', 'user_list': users})

# 랭킹 함수 : 게시물 개수별로 순위 랭킹하기
def select(YearNMonth):

#     year = str(datetime.now().year) if year is None else year
#     month = (str(datetime.now().month) if month is None else month).zfill(2)

#     post_date = '-'.join([year, month])
    print('YearNMonth',YearNMonth)
    pipeline = [
        {
            "$lookup": {
                "from": "userpost",
                "let": {"user_id": "$user_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$user_id", "$$user_id"]},
                                    {"$regexMatch": {
                                        "input": "$post_date",
                                        "regex": f"^{YearNMonth}"
                                    }}
                                ]
                            }
                        }
                    },
                    {
                        "$count": "cnt"
                    }
                ],
                "as": "posts"
            }
        },
        {
            "$unwind": {
                "path": "$posts",
                "preserveNullAndEmptyArrays": True
            }
        }
    ]

    results = list(db.user.aggregate(pipeline))  # 수정된 부분: 콜렉션 이름 변경

    results = [r for r in results if 'posts' in r]

    results = sorted(results,key=lambda x: x['posts']['cnt'], reverse=True)
#     print('results = ',results)
    ranked_data = []
    prev_cnt = None
    rank = 0

    print(results)

    for idx, r in enumerate(results):
        cnt = r['posts']['cnt']
        if cnt != prev_cnt:
            rank = idx + 1
        print('yqyq',  r['user_img_doc']['img_data'])
        ranked_data.append({
                "user_name": r['user_name'],
                "user_id": r['user_id'],
                "post_cnt": cnt,
                "user_url": r['user_url'],
                "user_img": "./static/img/default.jpg" if r.get('user_img_doc') is None or r['user_img_doc'].get('img_data') is None else r['user_img_doc']['img_data'] ,
                "rank": rank,
            })

        prev_cnt = cnt
    print('ranked_data=',ranked_data)
    return ranked_data

# API 3 : 랭킹함수 사용해보기
@app.route('/api/list/rank', methods=['GET'])
def show_rank():
    get_search_month = request.args.get('searchyearnmonth',datetime.today().strftime("%Y-%m"))

    posts_rank = select(get_search_month)

    return jsonify({'result': 'success', 'post_rank': posts_rank})


@app.route('/api/fight', methods=['POST'])
def insert_fight():

    # Retrieve POST parameters
    message = request.form.get('message')
    post_url = request.form.get('post_url')
    user = request.form.get('user')

    user_id =  db.userpost.find_one({'post_url':post_url})['user_id']



    # Insert the data into the 'postfight' collection
    db.postfight.insert_one({
        'message': message,
        'post_url': post_url,
        'user': user,
        'read' : 'N',
        'user_id' : user_id
    })

    print(message, post_url, user, user_id)

    return jsonify({'result': 'success'})


@app.route('/api/fight', methods=['GET'])
def show_fight():

    # Retrieve POST parameters
    post_url = request.args.get('post_url')


    postfight_list = db.postfight.find({'post_url':post_url})

    # print( list(postfight_list))

    return jsonify({'result': 'success' , 'message' : list(postfight_list) })


#안읽은 응원메시지 찾기

@app.route('/api/not_read')
def check_read():
    user_id = request.args.get('user_id')
    postfight_list = db.postfight.find({'user_id': user_id, 'read' : 'N' } )
    
    return jsonify({'result': 'success' , 'message' : list(postfight_list) })

@app.route('/api/read')
def update_read():
    id = request.args.get('id')
    print(id)
    result = db.postfight.update_one({'_id': ObjectId(id)}, {'$set': {'read': 'Y'}})

    return jsonify({'result': 'success'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug = True)