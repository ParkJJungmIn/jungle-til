import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from lxml import etree
from bson import ObjectId

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client['jungle7']                      # 'dbjungle'라는 이름의 db를 만듭니다.


def make_user():


    users_data = [
        {
            "user_id": "test1",
            "user_password": "password1",
            "user_gender": "M",
            "user_birth": "1990-01-01",
            "user_url": "https://park-dev-diary.tistory.com/",
            "user_lastpost": "",
            "user_name" : "박정민"
        },
        {
            "user_id": "test2",
            "user_password": "password1",
            "user_gender": "M",
            "user_birth": "1990-01-01",
            "user_url": "https://study4silver.tistory.com/",
            "user_lastpost": "",
            "user_name" : "전상하"
        },
        {
            "user_id": "test3",
            "user_password": "password1",
            "user_gender": "W",
            "user_birth": "1990-01-01",
            "user_url": "https://dev-dobim.tistory.com/",
            "user_lastpost": "",
            "user_name" : "조현지"
        },
    ]


    # db = client['jungle7']  # DB 이름 설정
    collection = db['user']  # 콜렉션 이름 설정
    collection.insert_many(users_data)


    userpost_data = [

        {
            "_id" : ObjectId(),
            "post_title" : "[백엔드] 기술 면접 Top30 - #30 정렬 알고리즘에 대해서",
            "post_url" : "https://dev-dobim.tistory.com/109",
            "user_id" : "test3",
            "post_date" : "2023-10-11"

        },

        {
            "_id" : ObjectId(),
            "post_title" : "[Python] @dataclass로 파이썬 클래스 마스터하기",
            "post_url" : "https://datasciencebeehive.tistory.com/4",
            "user_id" : "test2",
            "post_date" : "2023-10-12"

        },

        
        {
            "_id" : ObjectId(),
            "post_title" : "Python에서 while 반복문 사용법",
            "post_url" : "https://study4silver.tistory.com/207",
            "user_id" : "test1",
            "post_date" : "2023-10-13"

        },
    ]

    collection = db['userpost']  # 콜렉션 이름 설정
    collection.insert_many(userpost_data)


def select():
    pipeline = [
        {
            "$addFields": {
                "converted_date": {
                    "$dateFromString": {
                        "dateString": "$post_date",
                        "format": "%Y-%m-%d"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "year": { "$year": "$converted_date" },
                    "month": { "$month": "$converted_date" }
                },
                "count": { "$sum": 1 }
            }
        },
        {
            "$lookup": {
                "from": "user",  # 수정된 부분: 콜렉션 이름 변경
                "localField": "_id.user_id",
                "foreignField": "user_id",
                "as": "user_info"
            }
        },
        {
            "$unwind": "$user_info"
        },
        {
            "$sort": { "_id.user_id": 1, "_id.year": 1, "_id.month": 1 }
        }
    ]

    results = list(db.userpost.aggregate(pipeline))  # 수정된 부분: 콜렉션 이름 변경

    for result in results:
        print(result)

    


if __name__ == '__main__':
    # # 기존의 movies 콜렉션을 삭제하기
    # db.movies.drop()
    # # 영화 사이트를 scraping 해서 db 에 채우기
    # insert_all()
    # db = client['jungle7']  # DB 이름 설정
    # db.jungle7.drop()
    # make_user()
    select()
