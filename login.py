from bson import ObjectId
from pymongo import MongoClient
import requests
from lxml import etree
from flask import Flask, render_template, jsonify, request, render_template_string, make_response
from flask.json.provider import JSONProvider
from pprint import pprint
import json
import sys

import hashlib

from werkzeug.utils import secure_filename

from app_instance import *
from mongo_setup import get_db, get_secret_key
import os 

db = get_db()

@app.route('/login', methods=['GET'])
def get_login():    return render_template('login.html')

@app.route('/register', methods=['GET'])
def get_register():
    return render_template('register.html')

# 회원가입 이미지 업로드
@app.route('/register/imgupload', methods=['POST'])
def register_imgupload():
    print('11' , request.files)
    
    if "imageInput" in request.files:
        image = request.files.get("imageInput")
        print(image)
        print(type(image))

        filename = secure_filename(image.filename)
        return jsonify({'result': 'fail', 'upload_URL': filename})

# 회원가입
@app.route('/register', methods=['POST'])
def register_user():
    
    # 클라이언트에게서 데이터 받기
    input_img_receive = request.files.get("imageInput")
    user_id_receive = request.form['idInput']
    user_password_receive = request.form['passwordInput']
    user_name_receive = request.form['nameInput']
    user_gender_receive = request.form['genderInput']
    user_birth_receive = request.form['birthInput']
    user_url_receive = request.form['urlInput']
    
    #비밀번호 암호화
    user_password_encrypted =  hashlib.sha256(user_password_receive.encode('utf-8')).hexdigest()
    
    if (input_img_receive != None ):
        #이미지 저장을 위해 파일이름, 확장자를 알아내고, 경로를 설정한다
        filename = secure_filename(input_img_receive.filename)
        extension = filename.split(".")[-1]

        file_path = f"./static/profiles/{user_id_receive}.{extension}"

        #이미지 저장
        input_img_receive.save(file_path)
    
        #DB에 넣을 이미지 정보 설정
        user_img_doc = {
            "img_name": filename,
            "img_data": file_path,
        }
    else:
        user_img_doc = ""
    
    # DB에 넣을 데이터 정리
    user = {'user_id':user_id_receive, 'user_password' : user_password_encrypted,'user_name' : user_name_receive,
            'user_gender' : user_gender_receive,'user_birth' : user_birth_receive,'user_img_doc' : user_img_doc,'user_url' : user_url_receive,}
    
    print(user)
    # mongoDB에 데이터를 넣기
    if(db.user.insert_one(user)):
        #성공반환
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

#ID 중복확인
@app.route('/idcheck', methods=['POST'])
def id_check():
    # 클라이언트에게서 데이터 받기
    id_receive = request.form['user_id_give']
    
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
    
    #DB에서 아이디로 회원 조회
    checker = db.user.find_one({"user_id":id_receive})
    
    #DB에서 조회된 값이 있다면 비밀번호 확인
    if (checker.get('user_password')== password_encrypted):
        # JWT 토큰에는, payload와 시크릿키가 필요
        # 시크릿키가 있어야 토큰을 디코딩하여 payload 값을 확인 할 수 있음
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다(현재는 false). 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        access_token = create_access_token(identity = id_receive,
											expires_delta = False)
        
        return jsonify({'result': 'success', 'access_token' : access_token})
    
    else:
        return jsonify({'result': 'fail'})
    
#로그아웃
@app.route("/logout", methods=['POST'])
def log_out():
    # 제거할 토큰의 값을 가져온다
    token = request.cookies.get('Authorization')
    # 제거할 토큰의 값을 보낸다
    return jsonify({'result': 'success', 'access_token' : token})
    
