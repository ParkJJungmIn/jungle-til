from flask import Flask
from flask_jwt_extended import *

app = Flask(__name__)

# 토큰 생성에 사용될 Secret Key를 flask 환경 변수에 등록
app.config.update(
			DEBUG = True,
			JWT_SECRET_KEY = "I'M IML"
		)

# JWT 확장 모듈을 flask 어플리케이션에 등록
jwt = JWTManager(app)

def get_jwt():
    return jwt

