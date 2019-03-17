import requests
import pymongo
from multiprocessing.pool import Pool
from pyquery import PyQuery as pq
from requests import ConnectionError
from requests import Timeout
from urllib.parse import urlencode
import os
from hashlib import md5
from config import *

a = 0
client = pymongo.MongoClient(MONGO_URl)
db = client[MONGO_DB]

def get_index(page):
    URL = 'https://isujin.com/page/{}'.format(page)
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            html = response.text
            doc = pq(html)
            urls = doc('#primary .post > a').items()
            for url in urls:
                url = url.attr('href')
                yield url
            return doc('#post0 > h2 > a').attr('href')
    except ConnectionError:
        return None
def get_html(url):
    try:
        html = requests.get(url , timeout = 10)
        if html.status_code == 200:
            return html.text
        else:
            return None
    except ConnectionError as e:
        print("Error", e.args)
    except Timeout as t:
        print("Error", t.args)



#def change_page(html):
#    doc = pq(html)
#    next_url = doc('h3 > span > a:nth-child(2)').attr('href')
#    html = get_html(next_url)
#    return html


def parse_html(html):
    doc = pq(html)
    title = doc('.title').text()
    time = doc('div.stuff > span:nth-child(1)').text()
    readcount = doc('div.stuff > span:nth-child(2)').text()
    content = doc('.content').text()
    return {
        'title' : title,
        'time' : time,
        'readcount' : readcount,
        'content' : content
    }
def save_as_text(html):
    doc = pq(html)
    title = doc('.title').text()
    time = doc('div.stuff > span:nth-child(1)').text()
    readcount = doc('div.stuff > span:nth-child(2)').text()
    content = doc('.content').text()
    if not os.path.exists(title):
        os.mkdir(title)
    file_path = '{}/{}.txt'.format(title,title)
    if not os.path.exists(file_path):
        with open(file_path,'a',encoding='utf-8') as file:
            file.write('\n'.join([title, time, readcount,content]))
            print("Success",title)
def save_to_mongo(data):
    if db[MONGO_TABLE].update({'title' : data['title']},{'$set' : data}, True):
        print("Saved to Mongo", data['title'])
    else:
        print("Saved to Mongo Failed", data['title'])


def save_picture(html):
    global a
    doc = pq(html)
    images = doc('#jg > a').items()
    if not os.path.exists('picture'):
        os.mkdir('picture')
    for image in images:
        image = image.attr('href')
        try:
            response = requests.get(image)
            if response.status_code == 200:
                file_path = '{0}/{1}.jpg'.format('picture',md5(response.content).hexdigest())
                if not os.path.exists(file_path):
                    print("Downloading",file_path)
                    with open(file_path,'wb') as f:
                        f.write(response.content)
                else:
                    print("Already Downloaded",file_path)
                    a += 1
        except ConnectionError as e:
            print("Download Error", e.args)
def main(page):
    urls = get_index(page)
    for url in urls:
        html = get_html(url)
        if html:
            data = parse_html(html)
            if data:
                #save_as_text(html)
                save_to_mongo(data)# 如果没安装mongo可以取消此项
                #save_picture(html)

if __name__ == "__main__":

    pool = Pool()
    group = ([x for x in range(1,14)])
    pool.map(main,group)
    pool.close()
    pool.join()
    print(a)


