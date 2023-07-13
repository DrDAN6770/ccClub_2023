import requests
import googlemaps
import sqlite3
import pandas as pd
import dotenv
from Function_list import RoutePlanning

class CinemaFinder:
    def __init__(self,location):
        
        self.apikey = 'google-api'
        self.gmaps = googlemaps.Client(key='google-api')
        self.location = location

    # 取得規劃路線距離、估計時間
    def GM(self, destination, mode='driving'):
        response = self.gmaps.distance_matrix(self.location, destination, mode=mode)
        try:
            distance = response['rows'][0]['elements'][0]['distance']['value']
            duration = response['rows'][0]['elements'][0]['duration']['text']
            return distance, duration
        except:
            return None, None
    
    # 取得附近"直線距離"前6間電影院
    def MathJudge_dist(self, df):
        df['緯度'] = df['經緯度'].map(lambda x: float(x.split(',')[0])) - float(self.location.split(',')[0])
        df['經度'] = df['經緯度'].map(lambda x: float(x.split(',')[1])) - float(self.location.split(',')[1])
        df['直線距離'] = (df['緯度'] ** 2 + df['經度'] ** 2) ** 0.5
        df = df.drop(['緯度', '經度'], axis=1)
        df = df.sort_values(['直線距離']).reset_index(drop=True)
        return df.head(6)
    
    # 取得附近"交通距離"前3間電影院 & 規劃路線頁面
    def order_df_dist_google(self, df, mode='driving'):
        def format_RP_with_link(destination):
            url = RoutePlanning(self.location, destination)
            return f'{url}'

        # 取得place_id，將結果儲存成json格式
        def place_id_finder(place_name:str, lat:str, lng:str):
            # 取得地點資訊，將結果儲存成json格式
            url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place_name}&inputtype=textquery&fields=place_id&key={self.apikey}'
            payload = {}
            headers = {}
            response = requests.get(url, headers=headers, data=payload)
            add=f'{lat},{lng}'
            add=add.replace(' ','')
            # 從地點資訊中取得place_id
            info = response.json()
            place_id = info['candidates'][0]['place_id']
            place_url= f'https://www.google.com/maps/search/?api=1&query={add}&query_place_id={place_id}'
            # 輸出地點的map網址
            return f'{place_url}'

        # main
        df = df.copy()
        df['temp'] = df['經緯度'].map(lambda x: self.GM(x, mode))
        df['距離(公尺)'] = df['temp'].apply(lambda x: x[0])
        df['預計時間'] = df['temp'].apply(lambda x: x[1])
        df['路線規劃'] = df['事業名稱'].map(lambda x: format_RP_with_link(x))
        df['戲院googlemap'] = df.apply(lambda row: place_id_finder(row['事業名稱'], row['經緯度'].split(',')[0], row['經緯度'].split(',')[1]), axis=1)
        
        df.drop('temp', axis=1, inplace=True)
        #依照距離選出前三家電影院
        df = df.sort_values('距離(公尺)').reset_index(drop=True)
        res = df[['事業名稱', '距離(公尺)', '預計時間', '路線規劃', '戲院googlemap']].dropna().head(3)
        return res
    
    # 生成網頁表格
    def generate_html_table(self, df):
        html_table = df.to_html(index=False, escape=False)
        with open('CinemaFinder_table.html', 'w') as file:
            file.write(html_table)

location = '24.171550, 120.645647'

# 連線資料庫、SQL搜尋、轉df
conn = sqlite3.connect('C:/Users/zxc62/Downloads/Movie-20230703T224159Z-001/AMovie/TW_cinema_info.db')
data_df = pd.read_sql_query("SELECT * FROM TW_cinema_info_latest", conn)
conn.close()
# print(apikey)
# # 建立物件
finder = CinemaFinder( location)
filtered_data = finder.MathJudge_dist(data_df)
result = finder.order_df_dist_google(filtered_data)
result=result.to_dict()
