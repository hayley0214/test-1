import os
from flask import Flask, request, abort
from dotenv import load_dotenv
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()  # 讀取 .env

app = Flask(__name__)

# 環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    city_name = event.message.text.strip().replace("臺", "台")
    weather = get_weather(city_name)

    if weather:
        reply = f"{city_name}的天氣：{weather}"
    else:
        reply = "無法取得該城市的天氣資訊，請確認城市名稱是否正確。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

def get_weather(city):
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": city
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["success"] != "true":
            return None

        location_data = data["records"]["location"]
        if not location_data:
            return None

        weather_desc = location_data[0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        return weather_desc

    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

if __name__ == "__main__":
    app.run()
