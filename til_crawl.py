import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from lxml import etree

import time

client = MongoClient('mongodb://jungle:jungle@52.79.91.129/', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.jungle7

# userpost 기준으로 user_id의 최근 포스터들을 전부 가져온다

# 최근 포스터들에 1를 플러스하여 최신 포스터가 갱신되는지 확인한다
def fixed_url(url):
    index = url.find('.com') + 4
    trimmed_url = url[:index]

    return trimmed_url + '/'

# user_lastpost의 default를 1로 해놓는 것
def select_userpost():
    user_list = db.user.find()
    
    for user_row in user_list:
        missing_point = 0
        
        url = fixed_url(user_row['user_url'])
        user_lastpost = "1" if not user_row.get('user_lastpost') else user_row.get('user_lastpost')
        target_url = url + user_lastpost

        # 티스토리 경우 비공개 혹은 다른 이유로 url이 누락될 가능성을 최대 3번 놓칠 때 까지 크롤링 하기
        while missing_point < 3:
            crawl_return = crawl_userpost(target_url, user_row['user_id'])
            time.sleep(2)

            if crawl_return is False:
                missing_point += 1
            
# posturl 저장하기 이전에 한번 체크
def posturl_exists(post_url):
    userpost = db.userpost().find_one({'post_url' : post_url })
    return userpost is not None


def save_posturl(post_dict):
 print('a')




# 확인했을 때 새로운 포스터가 갱신되었다면 추가하면서 user 데이터도 같이 갱신한다
def crawl_userpost(target_url , user_id ):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(target_url, headers=headers)

    html_tree = etree.HTML( data.text )
    try:
        post_title = html_tree.xpath("//meta[@property='og:title']/@content")[0]
        post_url = html_tree.xpath("//meta[@property='og:url']/@content")[0]
        post_date = html_tree.xpath("//meta[@property='article:published_time']/@content")[0]

        post_date = post_date.split('T')[0]

    except:
        # 잘못된 페이지 만남
        return False
    
    # 데이터 저장 및 업데이트
    
    # 저장할 떄, url이 이미 저장되지 않았는지 체크 후
    if posturl_exists(post_url):
        return False
    

    post_data = { "post_title" : post_title , 
                 "post_url" : post_url ,
                  "post_date" : post_date,
                  "user_id" : user_id
                  }

    



    return True


crawl_userpost()
# select_userpost()

    


# user의 마지막포스트 번호가 없는 녀석들을 위주로 가져온다.

# 그냥 회원가입한 회원들은 전부 1번부터 다 데이터 크롤링하기

# 그리고 집계는 10월로 굳이 디테일하게 10일인 데이터들 삭제하거나 그런 작업 굳이 필요없을 듯
