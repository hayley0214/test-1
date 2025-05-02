from dotenv import load_dotenv
load_dotenv()

import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入環境變數
load_dotenv()

# 讀取憑證與金鑰
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")

# 初始化 LINE bot API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Flask 應用
app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    normalized_city = standardize_city_name(user_input)

    weather = get_weather(normalized_city)
    if weather:
        reply_text = f"{user_input} 的天氣：{weather}"
    else:
        reply_text = f"無法取得「{user_input}」的天氣資訊，請確認城市名稱。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def standardize_city_name(city):
    """ 將臺換成台，以符合中央氣象局資料格式 """
    return city.replace("臺", "台")

def get_weather(city_name):
    """ 從中央氣象局 API 取得指定城市天氣 """
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": city_name
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success") != "true":
            return None

        locations = data["records"].get("location", [])
        if not locations:
            return None

        return locations[0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API 請求失敗：{e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"[ERROR] 資料解析失敗：{e}")
        return None

if __name__ == "__main__":
    app.run()
