# from geopy.geocoders import Nominatim >>免費的，但地址輸入有限制 > 麻煩
from geopy.geocoders import GoogleV3
from geopy import distance
import dotenv
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import random

def get_latitude_longitude(address):
    # load .env
    info = dotenv.dotenv_values('.env')
    apikey = info.get('googleAPI')

    # geolocator = Nominatim(user_agent="my_app") # Nominatim
    geolocator = GoogleV3(api_key = apikey)
    location = geolocator.geocode(address)

    if location is not None:
        latitude = location.latitude  # 緯度
        longitude = location.longitude  # 經度
        return latitude, longitude
    else:
        return None
def distance_m(location1, location2):
    return distance.distance(location1, location2).meters if location1 and location2 else None

# 文字搜尋編碼化, 返回google map規劃路線網址(模式為:最佳)
def RoutePlanning(p1, p2):
    encoded_p1 = requests.utils.quote(p1)
    encoded_p2 = requests.utils.quote(p2)
    url = f'https://www.google.com/maps/dir/{encoded_p1}/{encoded_p2}'
    return url

# 返回電影院在google map上的連結
def place_url(r):
    # load .env
    info = dotenv.dotenv_values('.env')
    apikey = info.get('googleAPI')

    # 定義參數
    place_name = r['事業名稱']
    lat_n_lng = eval(r['經緯度'])
    lat = str(lat_n_lng[0])
    lng = str(lat_n_lng[1])

    # 取得地點資訊
    url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place_name}&inputtype=textquery&fields=place_id&key={apikey}'
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    # 從地點資訊中取得place_id
    place_info = response.json()
    place_id = place_info['candidates'][0]['place_id']

    place_url = f'https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={place_id}'
    return place_url

# 爬IMDb電影分類
def genres(query):
    # 搜尋電影
    header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    encoded_query = requests.utils.quote(query)
    url = f'https://www.imdb.com/find/?s=tt&q={encoded_query}&ref_=nv_sr_sm'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, "html.parser")

    res = soup.select_one('#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-5352556-0.cAzlUg > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section.ipc-page-section.ipc-page-section--base.sc-17bafbdb-0.eTBMbP > div.sc-17bafbdb-2.ffAEHI')
    R = res.select('ul > li > div > div > a')
    movie_link = None
    for i in R:
        if i.text.replace(' ','') == query.replace(' ',''):
            movie_link = f"https://www.imdb.com{i.get('href')}"
            break
    genres = []
    # 找該電影頁面
    if movie_link:
        sleep(random())
        response = requests.get(movie_link, headers=header)
        soup = BeautifulSoup(response.text, "html.parser")

        # 電影分類標籤
        res = soup.select_one('#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-f9e7f53-0.ifXVtO > section > div:nth-child(4) > section > section > div.sc-385ac629-4.dDTLMQ > div.sc-385ac629-6.nnaaE > div.sc-385ac629-10.SacCW > section > div.ipc-chip-list--baseAlt.ipc-chip-list > div.ipc-chip-list__scroller')
        if res:
            genres = [genre.text for genre in res.select('a')]
        else:
            res = soup.select_one('#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-f9e7f53-0.ifXVtO > section > div:nth-child(4) > section > section > div.sc-385ac629-4.dAacEl > div.sc-385ac629-6.lkFIWY > div.sc-385ac629-10.cbEKwe > section > div.ipc-chip-list--baseAlt.ipc-chip-list > div.ipc-chip-list__scroller')
            genres = [genre.text for genre in res.select('a')]
    
    return ', '.join(genres) if genres else 'No Genres'