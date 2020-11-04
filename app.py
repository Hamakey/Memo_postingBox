from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.memo


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')


## API 역할을 하는 부분
@app.route('/memo', methods=['POST'])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']  # 클라이언트로부터 url을 받는 부분
    comment_receive = request.form['comment_give']  # 클라이언트로부터 comment를 받는 부분
    # 2. url requests module 활용하여 get -> BeautifulSoup module을 이용하여
    # requests module로 불러온 정보를 html parser로 변환하여 저장함
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')  # 3. html 형태로 parsing하기 좋게 변형된 data에서 meta tag의 og:title property
    # 만 저장함(list 형태로 저장됨)
    og_title = soup.select_one('meta[property="og:title"]')
    og_image = soup.select_one('meta[property="og:image"]')
    og_description = soup.select_one('meta[property="og:description"]')
    # 4. 3에서 저장된 list형태의 data를 가지고
    title = og_title['content']
    image = og_image['content']
    description = og_description['content']

    # 5. mongoDB에 데이터를 넣기
    db.memo.insert_one(
        {'comment': comment_receive, 'url': url_receive, 'title': title, 'img': image, 'desc': description})

    return jsonify({'result': 'success'})


@app.route('/memo', methods=['GET'])
def listing():
    # 1. 모든 document 찾기 & _id 값은 출력에서 제외하기
    result = list(db.memo.find({}, {'_id': False}))

    # 2. articles라는 키 값으로 영화정보 내려주기

    return jsonify({'result': 'success', 'articles': result})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
