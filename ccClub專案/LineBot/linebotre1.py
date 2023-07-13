from flask import Flask, request, abort
import requests
import json
import sqlite3
import pandas as pd
import os
import re
from dotenv import load_dotenv
from urllib.parse import *
from random import random
from recommovie import Recommand_System
from pyngrok import ngrok,conf
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TemplateSendMessage,URIAction,ButtonsTemplate,PostbackEvent,StickerSendMessage,PostbackTemplateAction
from linebot.models import MessageEvent, TextMessage,TextSendMessage, StickerSendMessage, QuickReply, QuickReplyButton, MessageAction,FlexSendMessage
from sear import CinemaFinder
from searh import YahooMovies,IMDbMovies
from Function_list import RoutePlanning
config = load_dotenv(".env")
line_bot_api_ = os.getenv("line_bot_api")
handler_ = os.getenv("handler")

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
aa=menu()
fin=aa.find(':')
menunum=aa[(fin+2):-2]

# 輸入 Falsk
app = Flask(__name__)
ngrok.set_auth_token("2RdHs1UrRrb83ptGi03LZPOkCHs_6Cy2Tm1tNsZuBSEZdfCQN")
# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(line_bot_api_)
handler = WebhookHandler(handler_)
# 輸入 圖文選單 ID
with open('圖文選單.jpg', 'rb') as f:
    line_bot_api.set_rich_menu_image(menunum, 'image/jpeg', f)
headers = {'Authorization':'Bearer uT6QFkMstvp6mYFfIVWfXLBQYLzG2QWvsCqvHD8aiLKchArpOCiiPfF9jbcl+ozXMiHvm3ScesDW/f5419JPc0qP86/bKPetMPnvn2kkZx18z9skFHVjw7HxnsXJtoNe7pfHv/9EwtSGkLlTaLAmLgdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
req = requests.request('POST', f'https://api.line.me/v2/bot/user/all/richmenu/{menunum}', headers=headers)
#接收用戶端訊息
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    # handle webhook body
    try:
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)
    return 'OK'
#主程式
#接收訊息事件MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #回覆訊息之參數
    tk=event.reply_token
    mtext = event.message.text
    reply_msg = ''
    template_msg = '年度：\n中文片名：\n原文片名：\n國別：\n語言：\n類型：'
    if mtext[0:2]=="電影":
        try:
            YahooMovies_info = YahooMovies()
            userquery = YahooMovies_info.user_input(str(mtext[2:]))
            YahooMovies_info.search_movie(userquery)
            movielink=None
            moviecount=YahooMovies_info.search_movie(userquery)[1]
            movielink=YahooMovies_info.search_movie(userquery)[2]
            moviename=YahooMovies_info.search_movie(userquery)[3]
            print(movielink)
            # movie_titles=str(YahooMovies_info.search_movie(userquery)[0]) 
            # checkquery=str(YahooMovies_info.search_movie(userquery)[1])
            if moviecount>=3:
                reply_msg=[TextSendMessage(YahooMovies_info.search_movie(userquery)[0]),
                            TextSendMessage(text=f'找到{moviecount}部電影'),
                            TemplateSendMessage(
                                alt_text='Confirm Choice',
                                template=ButtonsTemplate(
                                    title='Choose one!',
                                    text='選你要的吧！',
                                    actions=[
                                        PostbackTemplateAction(
                                            label=f'{moviename[0]}',
                                            display_text=f'{moviename[0]}',
                                            data=f'Y{movielink[0]}&{moviename[0]}'
                                        ),
                                        PostbackTemplateAction(
                                            label=f'{moviename[1]}',
                                            display_text=f'{moviename[1]}',
                                            data=f'Y{movielink[1]}&{moviename[1]}'
                                        ),
                                        PostbackTemplateAction(
                                            label=f'{moviename[2]}',
                                            display_text=f'{moviename[2]}',
                                            data=f'Y{movielink[2]}&{moviename[2]}'
                                        ),                                    
                                    ]
                                ))
                                        ]
            elif moviecount==2:
                reply_msg=[TextSendMessage(YahooMovies_info.search_movie(userquery)[0]),
                            TextSendMessage(text=f'找到{moviecount}部電影'),
                            TemplateSendMessage(
                                alt_text='Confirm Choice',
                                template=ButtonsTemplate(
                                    title='Choose one!',
                                    text='選你要的吧！',
                                    actions=[
                                        PostbackTemplateAction(
                                            label=f'{moviename[0]}',
                                            display_text=f'{moviename[0]}',
                                            data=f'Y{movielink[0]}&{moviename[0]}'
                                        ),
                                        PostbackTemplateAction(
                                            label=f'{moviename[1]}',
                                            display_text=f'{moviename[1]}',
                                            data=f'Y{movielink[1]}&{moviename[1]}'
                                        ),                             
                                    ]
                                ))
                                        ]
            elif moviecount==1:
                reply_msg=[TextSendMessage(YahooMovies_info.search_movie(userquery)[0]),
                            TextSendMessage(text=f'找到{moviecount}部電影'),
                            TemplateSendMessage(
                                alt_text='Confirm Choice',
                                template=ButtonsTemplate(
                                    title='Choose one!',
                                    text='選你要的吧！',
                                    actions=[
                                        PostbackTemplateAction(
                                            label=f'{moviename[0]}',
                                            display_text=f'{moviename[0]}',
                                            data=f'Y{movielink}&{moviename[0]}'
                                        ),                               
                                    ]
                                ))
                                        ]
            else:
                reply_msg=TextSendMessage('抱歉搜尋不到您想要的結果!')
            line_bot_api.reply_message(tk, reply_msg)
        except TypeError:
            reply_msg=TextSendMessage('抱歉搜尋不到您想要的結果!')
            line_bot_api.reply_message(tk, reply_msg)
            return '找不到就是找不到'     
    elif mtext[0:6]=="直接推薦電影":
        try:
            RS = Recommand_System()
            reply=RS.random_recommand()
            reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=8525,sticker_id=16581294)]
            #回覆訊息之參數
            line_bot_api.reply_message(tk,reply_msg)

        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)

    elif mtext[0:6]=="我要看戲劇類":
        try:
            RS = Recommand_System()
            request = RS.cleanmsg('類型：Drama')
            reply=RS.random_recommand(request) 
            reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=6370,sticker_id=11088038)]
            line_bot_api.reply_message(tk,reply_msg)
        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)

    elif mtext[0:5]=="我要看喜劇類":
        try:
            RS = Recommand_System()
            request = RS.cleanmsg('類型：Comedy')
            reply=RS.random_recommand(request) 
            # reply_msg=f'{reply[0]} \n {reply[1]} \n {reply[2]}'
            reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=789,sticker_id=10857)]
            line_bot_api.reply_message(tk,reply_msg)
        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)

    elif mtext[0:6]=="我要看動作類":
        try:
            RS = Recommand_System()
            request = RS.cleanmsg('類型：Action')
            reply=RS.random_recommand(request)            
            reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=6632,sticker_id=11825385)]
            line_bot_api.reply_message(tk,reply_msg)
        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)

    elif mtext[0:6]=="我要看驚悚類":
        try:
            RS = Recommand_System()
            request = RS.cleanmsg('類型：Thriller')
            reply=RS.random_recommand(request)
            message=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=11539,sticker_id=52114139)]
            line_bot_api.reply_message(tk,message)
        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)
    elif mtext[0:7]=="我要看浪漫類":
        try:
            RS = Recommand_System()
            request = RS.cleanmsg('類型：Romance')
            reply=RS.random_recommand(request)
            reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=11539,sticker_id=52114118)]
            line_bot_api.reply_message(tk,reply_msg)
        except:
            reply_msg=[TextSendMessage(text='我壞掉了！搶救中'),StickerSendMessage(package_id=6632,sticker_id=11825391)]
            line_bot_api.reply_message(tk, reply_msg)     
    
    elif template_msg == re.sub(r'：.*?(?=\n|$)', '：', mtext):   
        mtext=mtext
        RS = Recommand_System()
        request = RS.cleanmsg(mtext)
        reply=RS.random_recommand(request)
        reply_msg=[TextSendMessage(text=reply[0]),TextSendMessage(text=reply[1]),TextSendMessage(text=reply[2]),StickerSendMessage(package_id=1070,sticker_id=17841)]
        line_bot_api.reply_message(tk,reply_msg)  
        
    else:
        try:
            reply_msg = TextSendMessage(
                text='抱歉我不懂您的意思，來看看電影吧！',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=URIAction(label='你要的都在這',uri='https://line.me/R/oaMessage/@708tiikx/?%E5%B9%B4%E5%BA%A6%EF%BC%9A%0A%E4%B8%AD%E6%96%87%E7%89%87%E5%90%8D%EF%BC%9A%0A%E5%8E%9F%E6%96%87%E7%89%87%E5%90%8D%EF%BC%9A%0A%E5%9C%8B%E5%88%A5%EF%BC%9A%0A%E8%AA%9E%E8%A8%80%EF%BC%9A%0A%E9%A1%9E%E5%9E%8B%EF%BC%9A')
                        ),
                        QuickReplyButton(
                            action=URIAction(label="點我看說明", uri="https://line.me/R/home/public/post?id=708tiikx&postId=1168913367039405093")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="戲劇類", text="我要看戲劇類")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="喜劇類", text="我要看喜劇類")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="動作類", text="我要看動作類")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="驚悚類", text="我要看驚悚類")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="浪漫類", text="我要看浪漫類")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(tk, reply_msg)
        except:
            line_bot_api.reply_message(tk, TextMessage(text='我壞掉了！搶救中')) 
    return 'OK'
#接收Postback事件觸發之事件
@handler.add(PostbackEvent)
def handle_postback(event):
    tk=event.reply_token
    #接收Postback事件觸發之參數
    ts = event.postback.data
    if ts[:1] =='Y':
        strindex=ts.find('&')
        YahooMovies_info=YahooMovies()
        movie_link=ts[1:strindex]
        movie_name=ts[(strindex+1):]
        movie_info =YahooMovies_info.specific_movie_info(movie_link)
        movie_info=str(movie_info)
        IMDbMovies_info = IMDbMovies(movie_name)
        if  IMDbMovies_info=='' or IMDbMovies_info==None:
            reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text='目前IMDb尚無評論！！')]
        else:
            IMDb_results = IMDbMovies_info.search_movie(IMDbMovies_info.yahoosearchname)
            if IMDb_results[0]==0 :
                reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text='目前IMDb尚無評論！！')]
                
            elif IMDb_results[0]==1:
                IMDb_link=IMDb_results[2]
                IMDb_reviews=str(IMDbMovies_info.specific_movie_reviews(IMDb_link))
                if IMDb_reviews==None or IMDb_reviews=='':
                    reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text='目前IMDb尚無評論！！')]
                else:
                    reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text=IMDb_reviews)]
            elif IMDb_results[0]>=2:
                IMDb_link=IMDb_results[2][0]
                IMDb_reviews=str(IMDbMovies_info.specific_movie_reviews(IMDb_link))
                if IMDb_reviews==None or IMDb_reviews=='':
                    reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text='目前IMDb尚無評論！！')]
                else:
                    reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text=IMDb_reviews)]                
            else:
                reply_msg=[TextSendMessage(text=movie_info),TextSendMessage(text='目前IMDb尚無評論！！')]

    elif ts=='@M1':
        reply_msg = FlexSendMessage(alt_text='您有新訊息',
                        contents={"type": "carousel",
                        "contents":[{
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "電影迷尋蹤",
                                "weight": "bold",
                                "size": "xl"
                            },
                            {
                                "type": "text",
                                "text": "點擊這邊可以知道更多",
                                "color": "#7B7B7B"
                            }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                "type": "uri",
                                "label": "想了解更多點這邊",
                                "uri": "https://line.me/R/home/public/post?id=708tiikx&postId=1168913367039405093"
                                }
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "uri",
                                "label": "快寫下你想要的吧",
                                "uri": "https://line.me/R/oaMessage/@708tiikx/?%E5%B9%B4%E5%BA%A6%EF%BC%9A%0A%E4%B8%AD%E6%96%87%E7%89%87%E5%90%8D%EF%BC%9A%0A%E5%8E%9F%E6%96%87%E7%89%87%E5%90%8D%EF%BC%9A%0A%E5%9C%8B%E5%88%A5%EF%BC%9A%0A%E8%AA%9E%E8%A8%80%EF%BC%9A%0A%E9%A1%9E%E5%9E%8B%EF%BC%9A"
                                },
                                "style": "secondary"
                            }
                            ],
                            "flex": 0
                        }
                        }]})        
    else:
        reply_msg=TextSendMessage(text='出錯了，請稍等')
    line_bot_api.reply_message(tk, reply_msg)
        
@handler.add(MessageEvent)
def handle_message1(event):
    tk=event.reply_token
    if event.message.type=='location':
        try:
            #擷取經緯度event.message.latitude,event.message.longitude
            location = '{},{}'.format(event.message.latitude,event.message.longitude)
            #連接資料庫
            conn = sqlite3.connect('C:/Users/zxc62/Downloads/Movie-20230703T224159Z-001/AMovie/TW_cinema_info.db')
            data_df = pd.read_sql_query("SELECT * FROM TW_cinema_info_latest", conn)
            conn.close()
            # 建立物件
            finder = CinemaFinder(location)
            filtered_data = finder.MathJudge_dist(data_df)
            result = finder.order_df_dist_google(filtered_data)
            #將回傳數值轉成字串
            result=result.to_dict()
            flex_message = FlexSendMessage(alt_text='您有新訊息',
                                        contents={"type": "carousel",
                                                "contents": [{
                                                "type": "bubble",
                                                "size": "micro",
                                                "hero": {
                                                "type": "image",
                                                "url": "https://images.pexels.com/photos/9433910/pexels-photo-9433910.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                                                "size": "full",
                                                "aspectMode": "cover",
                                                "aspectRatio": "320:213"
                                                            },
                                                            "body": {
                                                                "type": "box",
                                                                "layout": "vertical",
                                                                "contents": [{
                                                                    "type": "text",
                                                                    "text": str(result['事業名稱'][0]),
                                                                    "weight": "bold",
                                                                    "size": "sm",
                                                                    "wrap": True
                                                                }, {
                                                                    "type": "box",
                                                                    "layout": "vertical",
                                                                    "contents": [{
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "spacing": "sm",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "距離",
                                                                            "wrap": True,
                                                                            "size": "sm",
                                                                            "flex": 5,
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['距離(公尺)'][0]),
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "預計時間",
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['預計時間'][0]),
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "點我規劃",
                                                                                "uri":str(result['路線規劃'][0])
                                                                            }
                                                                        }, {
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "你想要的在這",
                                                                                "uri":str(result['戲院googlemap'][0])
                                                                            }
                                                                        }]
                                                                    }]
                                                                }],
                                                                "spacing": "sm",
                                                                "paddingAll": "13px"
                                                            }
                                                        }, {
                                                            "type": "bubble",
                                                            "size": "micro",
                                                            "hero": {
                                                                "type": "image",
                                                                "url": "https://images.pexels.com/photos/2873486/pexels-photo-2873486.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                                                                "size": "full",
                                                                "aspectMode": "cover",
                                                                "aspectRatio": "320:213"
                                                            },
                                                            "body": {
                                                                "type": "box",
                                                                "layout": "vertical",
                                                                "contents": [{
                                                                    "type": "text",
                                                                    "text": str(result['事業名稱'][1]),
                                                                    "weight": "bold",
                                                                    "size": "sm",
                                                                    "wrap": True
                                                                }, {
                                                                    "type": "box",
                                                                    "layout": "vertical",
                                                                    "contents": [{
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "spacing": "sm",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "距離",
                                                                            "size": "sm",
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['距離(公尺)'][1]),
                                                                            "size": "sm",
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "預計時間",
                                                                            "size": "sm",
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['預計時間'][1]),
                                                                            "size": "sm",
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "點我規劃",
                                                                                "uri":str(result['路線規劃'][1])
                                                                            }
                                                                        }, {
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "你想要的在這",
                                                                                "uri":str(result['戲院googlemap'][1])
                                                                            }
                                                                        }]
                                                                    }]
                                                                }],
                                                                "spacing": "sm",
                                                                "paddingAll": "13px"
                                                            }
                                                        }, {
                                                            "type": "bubble",
                                                            "size": "micro",
                                                            "hero": {
                                                                "type": "image",
                                                                "url": "https://images.pexels.com/photos/7991525/pexels-photo-7991525.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                                                                "size": "full",
                                                                "aspectMode": "cover",
                                                                "aspectRatio": "320:213"
                                                            },
                                                            "body": {
                                                                "type": "box",
                                                                "layout": "vertical",
                                                                "contents": [{
                                                                    "type": "text",
                                                                    "text": str(result['事業名稱'][2]),
                                                                    "weight": "bold",
                                                                    "size": "sm"
                                                                }, {
                                                                    "type": "box",
                                                                    "layout": "vertical",
                                                                    "contents": [{
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "spacing": "sm",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "距離",
                                                                            "size": "sm",
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['距離(公尺)'][2]),
                                                                            "size": "sm",
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "text",
                                                                            "text": "預計時間",
                                                                            "size": "sm",
                                                                            "weight": "bold"
                                                                        }, {
                                                                            "type": "text",
                                                                            "text": str(result['預計時間'][2]),
                                                                            "size": "sm",
                                                                            "color": "#8c8c8c"
                                                                        }]
                                                                    }, {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [{
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "點我規劃",
                                                                                "uri": str(result['路線規劃'][2])
                                                                            }
                                                                        }, {
                                                                            "type": "button",
                                                                            "action": {
                                                                                "type": "uri",
                                                                                "label": "你想要的在這",
                                                                                "uri":str(result['戲院googlemap'][2])
                                                                            },
                                                                            "margin": "none"
                                                                        }]
                                                                    }]
                                                                }],
                                                                "spacing": "sm",
                                                                "paddingAll": "13px"
                                                            }
                                                        }]
                                                    })
            line_bot_api.reply_message(tk, flex_message)
        except:
            print('位置有問題！！')
    else:
        try:
            line_bot_api.reply_message(tk, TextSendMessage(text='出錯了，請稍等'))
        except:
            print('firstunknow!!!')

if __name__ == "__main__":
    app.run() 
