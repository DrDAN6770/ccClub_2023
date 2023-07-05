import requests
from bs4 import BeautifulSoup
from time import sleep
from random import random
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