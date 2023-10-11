import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from lxml import etree
from bson import ObjectId

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
# db = client.dbtil                      # 'dbjungle'라는 이름의 db를 만듭니다.


def make_user():


    users_data = [
        {
            "user_id": "test1",
            "user_password": "password1",
            "user_gender": "Male",
            "user_birth": "1990-01-01",
            "user_url": "https://park-dev-diary.tistory.com/",
            "user_lastpost": "",
            "user_name" : "박정민"
        },
        {
            "user_id": "test2",
            "user_password": "password1",
            "user_gender": "Male",
            "user_birth": "1990-01-01",
            "user_url": "https://study4silver.tistory.com/",
            "user_lastpost": "",
            "user_name" : "전상하"
        },
        {
            "user_id": "test3",
            "user_password": "password1",
            "user_gender": "FeMale",
            "user_birth": "1990-01-01",
            "user_url": "https://dev-dobim.tistory.com/",
            "user_lastpost": "",
            "user_name" : "조현지"
        },
    ]


    db = client['jungle7']  # DB 이름 설정
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






    


    

def insert_all():
    # URL을 읽어서 HTML를 받아오고,
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.daum.net/ranking/boxoffice/yearly', headers=headers)

    html_tree = etree.HTML( data.text )
    movie_list = html_tree.xpath("//ol[@class='list_movieranking']/li")

    for movie_tree in movie_list:

        title = movie_tree.xpath(".//a[@class='link_txt']")[0].text
        link = movie_tree.xpath(".//a[@class='link_txt']/@href")[0]
        open_date = movie_tree.xpath(".//span[@class='info_txt'][1]/span" )[0].text
        people = movie_tree.xpath(".//span[@class='info_txt'][2]")[0]
        people = [ t for t in people.itertext()][1]
        poster_url = movie_tree.xpath(".//img/@src")[0]

        open_year, open_month, open_day = map(int,open_date.split('.'))
        open_year += 2000

        link = 'https://movie.daum.net' + link
         
        viewers =  ''.join(filter(str.isdigit, people))
        
        doc = { 
            'title': title,
            'open_year': open_year,
            'open_month': open_month,
            'open_day': open_day,
            'viewers': int(viewers),
            'poster_url' : poster_url,
            'trashed' : False,
            'like' : 0,
            'link' : link
        }   

        db.movies.insert_one(doc)
        print('완료: ', title, open_year, open_month, open_day, viewers)

if __name__ == '__main__':
    # # 기존의 movies 콜렉션을 삭제하기
    # db.movies.drop()
    # # 영화 사이트를 scraping 해서 db 에 채우기
    # insert_all()
    db = client['jungle7']  # DB 이름 설정
    db.jungle7.drop()
    make_user()