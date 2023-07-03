# from geopy.geocoders import Nominatim >>免費的，但地址輸入有限制 > 麻煩
from geopy.geocoders import GoogleV3
from geopy import distance
import dotenv
import requests

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