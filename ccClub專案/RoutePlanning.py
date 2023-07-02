import requests
# 文字搜尋編碼化, 返回google map規劃路線網址(模式為:最佳)
def RP(p1, p2):
    encoded_p1 = requests.utils.quote(p1)
    encoded_p2 = requests.utils.quote(p2)
    url = f'https://www.google.com/maps/dir/{encoded_p1}/{encoded_p2}'
    return url