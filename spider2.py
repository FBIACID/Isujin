import requests
from pyquery import PyQuery as pq
from requests import ConnectionError
from requests import Timeout
from multiprocessing.pool import Pool
from hashlib import md5
import os

def get_index(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        }
        response = requests.get(url = url,headers = headers,timeout = 5)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except ConnectionError as e:
        print("Error",e.args)
    except Timeout as t:
        print("Error",t.args)
def parse_index(html):
    doc = pq(html)
    urls = doc('a.preview').items()
    for url in urls:
        number = url.attr('href').replace("https://alpha.wallhaven.cc/wallpaper/","")
        yield number
def save(url):
    image = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-" + url + ".jpg"
    try:
        response = requests.get(image)
        if response.status_code == 200:
            file_path = '{0}/{1}.jpg'.format('pic', md5(response.content).hexdigest())
            if not os.path.exists(file_path):
                print("Downloading", file_path)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print("Already Downloaded", file_path)
    except ConnectionError as e:
        print("Download Error", e.args)


def main(number):
    url = "https://alpha.wallhaven.cc/toplist?page=" + str(number)
    html = get_index(url)
    if html:
        urls = parse_index(html)
        for url in urls:
            save(url)

if __name__ == "__main__":
    pool = Pool()
    group = ([x for x in range(1,50)])
    pool.map(main, group)
    pool.close()
    pool.join()




