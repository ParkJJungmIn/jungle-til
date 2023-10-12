from bson import ObjectId
from pymongo import MongoClient
import requests
from lxml import etree
from flask import Flask, render_template, jsonify, request, render_template_string
from flask.json.provider import JSONProvider
from pprint import pprint
import json
import sys

import jwt
import datetime
import hashlib

from app_instance import app
from mongo_setup import get_db

db = get_db()

#JWT 토큰을 만들기 위해 필요한 비밀문자열 - 아무거나 입력해도 된다
#서버 내에만 저장되기에 이 서버 내에서만 인코딩 디코딩 할 수 있게 해준다
SECRET_KEY = 'JUNGLE'

@app.route('/login', methods=['GET'])
def get_login():    return render_template('login.html')

@app.route('/register', methods=['GET'])
def get_register():
    return render_template('register.html')

# 회원가입
@app.route('/register', methods=['POST'])
def register_user():
    # 클라이언트에게서 데이터 받기
    user_id_receive = request.form['user_id_register']
    user_password_receive = request.form['user_password_register']
    user_name_receive = request.form['user_name_register']
    user_gender_receive = request.form['user_gender_register']
    user_birth_receive = request.form['user_birth_register']
    user_url_receive = request.form['user_url_register']
    
    #비밀번호 암호화
    user_password_encrypted =  hashlib.sha256(user_password_receive.encode('utf-8')).hexdigest()

    # DB에 넣을 데이터 정리
    user = {'user_id':user_id_receive, 'user_password' : user_password_encrypted,'user_name' : user_name_receive,
            'user_gender' : user_gender_receive,'user_birth' : user_birth_receive,'user_url' : user_url_receive,}
    
    # mongoDB에 데이터를 넣기
    db.user.insert_one(user)

    #성공반환
    return jsonify({'result': 'success'})

#ID 중복확인
@app.route('/idcheck', methods=['POST'])
def id_check():
    # 클라이언트에게서 데이터 받기
    id_receive = request.form['user_id_give']
    
    print(id_receive)
    
    #DB에서 id와 같은값이 있다면 실패, 없다면 성공 반환
    if(db.user.find_one({"user_id":id_receive})):
        return jsonify({'result': 'fail'})
    else:
        return jsonify({'result': 'success'})
        

#로그인
@app.route('/login', methods=['POST'])
def log_in():
    # 클라이언트에게서 데이터 받기
    id_receive = request.form['user_id_give']
    password_receive = request.form['user_password_give']
    
    #비밀번호 암호화
    password_encrypted = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    
    #DB에서 아이디와 암호화된 비밀번호로 회원 조회
    checker = db.user.find_one({"user_id":id_receive},{'user_password':password_encrypted})
    
    #DB에서 조회된 값이 있다면
    if checker is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요
        # 시크릿키가 있어야 토큰을 디코딩하여 payload 값을 확인 할 수 있음
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다(5초). 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token' : token})
    
    else:
        return jsonify({'result': 'fail'})

#토큰 유효성 검사
def check_token(token):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        #얼마 안남았을 때 30분 이하
        if payload['exp'] + datetime.timedelta(minutes=30)< datetime.datetime.now():
            refreshed = refresh_token(token)
            return refreshed
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return False
    except jwt.exceptions.DecodeError:
        return False
    
    #아무 이상없다면
    return True

def refresh_token(token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        newpayload = {
            'id': payload['id'] ,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }
        newtoken = jwt.encode(newpayload, SECRET_KEY, algorithm='HS256')
        return newtoken
    