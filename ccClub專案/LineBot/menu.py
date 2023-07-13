import requests
import json
def menu():
# 輸入 Access Token，記得前方要加上「Bearer 」( 有一個空白 )
    headers = {'Authorization':'Bearer uT6QFkMstvp6mYFfIVWfXLBQYLzG2QWvsCqvHD8aiLKchArpOCiiPfF9jbcl+ozXMiHvm3ScesDW/f5419JPc0qP86/bKPetMPnvn2kkZx18z9skFHVjw7HxnsXJtoNe7pfHv/9EwtSGkLlTaLAmLgdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}

    # 需補上'action'設定
    body = {
        'size': {'width': 1250, 'height': 843},   # 設定尺寸
        'selected': 'true',                        # 預設是否顯示
        'name': 'movie bot menu',                   # 選單名稱
        'chatBarText': 'Movie Bot Menu',            # 選單在 LINE 顯示的標題
        'areas':[                                  # 選單內容
            {
            'bounds': {'x': 5, 'y': 0, 'width': 406, 'height': 843}, # 選單位置與大小
            'action': { "type": "uri","label": "Location",'uri':'https://line.me/R/nv/location'} # 點擊地標圖示後的動作
            },
            {
            'bounds': {'x': 421, 'y': 0, 'width': 406, 'height': 843},
            'action': {  "type": "postback","label":"我想看更多","data":"@M1"} # 點擊隨機圖示後的動作
            },
            {
            'bounds': {'x': 837, 'y': 0, 'width':406, 'height': 843},
            'action': { 'type': 'uri', 'label': '點我推薦', 'uri':'https://line.me/R/oaMessage/@708tiikx/?%E9%9B%BB%E5%BD%B1'}  # 點擊放大鏡圖示後的動作
            }
        ]
    }
    # 向指定網址發送 request
    req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',headers=headers,data=json.dumps(body).encode('utf-8'))
    return req.text
print(menu())

