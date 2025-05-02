from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os
from dotenv import load_dotenv

# 讀取 .env 環境變數
load_dotenv()

app = Flask(__name__)

# 環境變數（請先設在 .env 或 Render 設定中）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 中央氣象局 API URL（36小時天氣預報）
CWB_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

def get_weather(city):
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": city
    }
    try:
        response = requests.get(CWB_URL, params=params)
        data = response.json()
        location_data = data["records"]["location"][0]
        city_name = location_data["locationName"]
        weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        return f"{city_name} 的天氣是：{weather}"
    except Exception:
        return "查無此城市或氣象資料有誤，請重新輸入！"

@app.route("/", methods=['GET'])
def index():
    return "LINE Bot 天氣查詢服務運作中"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    city = event.message.text.strip()
    weather_info = get_weather(city)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=weather_info)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
