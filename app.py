import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# LINE 憑證從 .env 讀取
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 城市名稱對應表
city_aliases = {
    "台北": "臺北市", "台北市": "臺北市",
    "台中": "臺中市", "台中市": "臺中市",
    "台南": "臺南市", "台南市": "臺南市",
    "高雄": "高雄市", "高雄市": "高雄市",
    "新北": "新北市", "新北": "新北市",
    "桃園": "桃園市", "桃園市": "桃園市",
    "基隆": "基隆市", "基隆市": "基隆市",
    "新竹": "新竹市", "新竹市": "新竹市",
    "嘉義": "嘉義市", "嘉義市": "嘉義市",
    "宜蘭": "宜蘭縣", "宜蘭縣": "宜蘭縣",
    "花蓮": "花蓮縣", "花蓮縣": "花蓮縣",
    "台東": "臺東縣", "台東縣": "臺東縣",
}

def get_weather(city):
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        locations = data['records']['location']

        for location in locations:
            if location['locationName'] == city:
                weather = location['weatherElement'][0]['time'][0]['parameter']['parameterName']
                rain = location['weatherElement'][1]['time'][0]['parameter']['parameterName']
                temp_min = location['weatherElement'][2]['time'][0]['parameter']['parameterName']
                temp_max = location['weatherElement'][4]['time'][0]['parameter']['parameterName']
                return f"{weather}，降雨機率 {rain}%，氣溫 {temp_min}°C - {temp_max}°C"
        return None
    except Exception as e:
        print("Error fetching weather:", e)
        return None

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
    user_text = event.message.text.strip()
    city_name = city_aliases.get(user_text, user_text)  # 標準化

    weather_data = get_weather(city_name)

    if weather_data:
        reply = f"{city_name} 天氣資訊：\n{weather_data}"
    else:
        reply = f"找不到「{user_text}」的天氣資訊，請輸入正確的城市名稱。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
