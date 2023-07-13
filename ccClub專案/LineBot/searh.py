import requests
import re
from bs4 import BeautifulSoup
from time import sleep
from random import random
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage# 載入 TextSendMessage 模組
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage, StickerSendMessage,LocationSendMessage, QuickReply, QuickReplyButton, MessageAction,FlexSendMessage
import json
# YahooMovies 邏輯 : 使用者輸入 > 搜尋電影 > 確認哪一部(沒有就重找or沒有這部) > 找這部資訊 > 返回搜尋結果
# IMDbMovies 邏輯 : 從YahooMovies拿完整確定查找的電影名稱(有不同或多選擇需要使用者去Y/N決定) > 搜尋該電影評論 > 返回資訊
class YahooMovies():
    def __init__(self):
        self.movie_link = None

    def user_input(self, movie_name): # 返回使用者輸入的電影名稱(可能不是完整電影名)
        while True:
            try:
                movie_name = movie_name
                if movie_name.strip():
                    return movie_name
            except:
                print('\nTry Again')
                return None

    def search_movie(self, userquery): # 返回搜尋列表、使用者查的電影名稱(可能不是完整電影名)
        encoded_query = requests.utils.quote(userquery)
        url = f"https://movies.yahoo.com.tw/moviesearch_result.html?keyword={encoded_query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        movie_titles = soup.find_all("div", class_="release_movie_name")
        movie_urls=[]
        movie_yahoo_titles=[]
        movie_titles_string = ""
        i=0
        # movie_links = soup.select(".release_movie_name a")
        res_count=len(movie_titles)
        if res_count==0:
            return "", 0, [], []
        #超過1筆以上
        elif res_count>=2: 
            
            
            if res_count>=3:
                res_count=3
            #數量
            count=res_count
            
            #網址
            for div in soup.find_all('div', class_='release_movie_name'):
                if len(movie_urls)==4:
                    break
                movie_urls.append(div.a['href'])
            #電影標題    
            for font in soup.find_all('font', class_='highlight'):
                text = f'{font.string}{font.find_next_sibling(string=True)}'
                if len(movie_yahoo_titles)==4:
                    break
                movie_yahoo_titles.append(text)
                
            #linebot能接受之訊息格式
            for i,title in enumerate(movie_titles, 1):
                if i==4:
                    break
                astr=title.get_text().rstrip()
                movie_titles_string += f"第{i}筆. {astr}\n"
            movie_titles_string= movie_titles_string.split('\n') 
            movie_titles_string = [line.strip() for line in movie_titles_string if line.strip()]
            movie_titles_string= '\n'.join(movie_titles_string) 
            pattern = r'第\d+筆\.\n(.+?)\n'
            movie_yahoo_titles = re.findall(pattern, movie_titles_string, re.DOTALL)  # 使用re.findall找到符合條件的所有電影標題
            

            return movie_titles_string, count, movie_urls, movie_yahoo_titles
        #數量等於1筆
        elif res_count==1:
            
            #數量
            count=res_count
            
            #網址
            movie_urls=movie_titles[0].a['href']
            
            
            #linebot能接受之訊息格式
            for i,title in enumerate(movie_titles, 1):
                astr=title.get_text().rstrip()
                movie_titles_string += f"第{i}筆. {astr}\n"
            movie_titles_string= movie_titles_string.split('\n') 
            movie_titles_string = [line.strip() for line in movie_titles_string if line.strip()]
            movie_titles_string= '\n'.join(movie_titles_string) 
            pattern = r'第\d+筆\.\n(.+?)\n'
            movie_yahoo_titles = re.findall(pattern, movie_titles_string, re.DOTALL)  # 使用re.findall找到符合條件的所有電影標題
            
            
            return movie_titles_string, count, movie_titles[0].a['href'], movie_yahoo_titles
        else:
            return "", 0, [], []
    
    def specific_movie_info(self, movie_link): # 返回這部電影所需的資訊
        def review_latest(review_link):
            if review_link is None:
                return None
            res = []
            response = requests.get(review_link)
            soup = BeautifulSoup(response.text, "html.parser")
            reviews = soup.find_all('div', class_='usercom_inner _c')
            
            review_counts=0
            for i in reviews:
                if review_counts == 5: 
                    break
                content = re.sub(r'[\s]{2,}|[\n\r\t]+', '', i.find_all('span')[-1].text)
                #排除廣告評論
                pattern = re.compile(r'(微信|line|外約|娛樂城|私聊)', re.IGNORECASE)
                if pattern.search(content): 
                    continue

                res.append(content)
                review_counts += 1
            return res if res else '該電影目前無評論'

        movie_info = {}
        if movie_link:
            response = requests.get(movie_link)
            soup = BeautifulSoup(response.text, "html.parser")
            movie = soup.find('div', class_='movie_intro_info_r')
            review = soup.find('div', class_='btn_plus_more usercom_more gabtn')
            review_link = review.a['href'] if review else None
            starscore = soup.find('div', class_='score_num count')
            starbox = soup.find('div', class_='starbox2')

            chname = re.sub(r'[\s]{2,}|[\n\r\t]+', '', movie.h1.text)
            engname = re.sub(r'[\s]{2,}|[\n\r\t]+', '', movie.h3.text) if movie.h3.text else None

            if starscore and starbox:
                starscore = f'{starscore.text} / 5 {starbox.text.strip()}'
            else:
                starscore = None

            reviews = review_latest(review_link)

            release_date, IMDB = None, None
            for i in movie.find_all('span'):
                text = i.text.strip()
                if '上映日期' in text:
                    release_date = text.split('：')[1]
                elif 'IMDb分數' in text:
                    IMDB = f"{text.split('：')[1]} / 10"
            movie_info['中文名稱'] = chname
            movie_info['英文名稱'] = engname
            movie_info['上映日期'] = release_date
            movie_info['滿意度'] = starscore
            movie_info['IMDb'] = IMDB
            movie_info['Yahoo最新評論'] = reviews

            return movie_info

class IMDbMovies(YahooMovies):
    def __init__(self, name):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.yahoosearchname = name        # Yahoo找到完整電影名稱(不是使用者輸入的)

    def specific_movie_reviews(self, movie_link): # 返回電影評論list
        response = requests.get(movie_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        reviews = soup.find_all('div', class_='review-container')

        movie_reviews = []
        for review in reviews[:5]:
            review_title = review.find('a', class_='title').text.strip()
            movie_reviews.append(review_title)
        return movie_reviews if movie_reviews else None

    def search_movie(self, query): # 返回電影評論網址
        # search
        encoded_query = requests.utils.quote(query)
        url = f"https://www.imdb.com/find/?q={encoded_query}&ref_=nv_sr_sm"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.select('#__next > main > div.ipc-page-content-container.ipc-page-content-container--full.sc-5352556-0.cAzlUg > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid__item.ipc-page-grid__item--span-2 > section:nth-child(3) > div.sc-17bafbdb-2.ffAEHI > ul > li')
        # check search list
        if search_results:
            search_count = len(search_results)
            movie = search_results[0]
            k = movie.select_one('div > div > a')
            movie_number = k.get('href').split('/')[2]
            review_link = f'https://www.imdb.com/title/{movie_number}/reviews?ref_=tt_urv'
            if query == k.text:
                return 1,k.text,review_link
            if search_count > 1:
                name=[]
                link=[]
                for m in search_results:
                    k = m.select_one('div > div > a')
                    movie_number = k.get('href').split('/')[2]
                    review_link = f'https://www.imdb.com/title/{movie_number}/reviews?ref_=tt_urv'
                    name.append(k.text)
                    link.append(review_link)
                    print(k.text,'m',review_link)
                # 該次搜尋都沒找到，重新搜尋
                return search_count,name,link
        else:
            return 0,None,None


