import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from lxml import etree

client = MongoClient('mongodb://jm:jm@0.0.0.0:27017/', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle                      # 'dbjungle'라는 이름의 db를 만듭니다.


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
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()
    # 영화 사이트를 scraping 해서 db 에 채우기
    insert_all()