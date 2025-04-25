import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 從環境變數取得 LINE 憑證
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 中央氣象局 API Key（可直接寫死或改用環境變數）
CWB_API_KEY = "CWA-6DA407C7-D330-4E0C-BBEC-2DA1F6B260EA"

@app.route("/")
def home():
    return "LINE Bot with CWB Weather is running!"

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
    weather = get_weather(city)
    reply = weather if weather else f"找不到 {city} 的天氣資訊，請確認輸入正確的縣市名稱（例如：台北、高雄）"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

def get_weather(city):
    url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": city
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return None

    data = res.json()
    try:
        location_data = data["records"]["location"][0]
        city_name = location_data["locationName"]
        wx = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        pop = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        min_temp = location_data["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
        max_temp = location_data["weatherElement"][4]["time"][0]["parameter"]["parameterName"]

        return f"{city_name} 天氣：{wx}\n降雨機率：{pop}%\n氣溫：{min_temp}°C - {max_temp}°C"
    except Exception as e:
        return None

if __name__ == "__main__":
    app.run()
