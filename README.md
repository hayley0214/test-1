# test-1
import requests
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設定 LINE API
LINE_CHANNEL_ACCESS_TOKEN = "Cyez3SBJqPIV3Jyrf58MzwJAEkVpf+OvcMN1Wv6h0qry8KV0zwSKj6q9neuttVdUu5re7+BorLXfj0rmDIfGvYwQ/kyrd1DTQgNh25XAouoB4nerJ8jSPTB3rQJtsoFeSkAA3PAEAB+lndQEQujRSQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "e01ae91e66566f00e45594e223afa0f6"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 建立 Flask 伺服器
app = Flask(__name__)

# 取得天氣資訊（使用 CWB API）
def get_weather(city):
    API_KEY = "CWA-6DA407C7-D330-4E0C-BBEC-2DA1F6B260EA"
    url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={API_KEY}&format=JSON"
    
    response = requests.get(url)
    data = response.json()
    
    for location in data["records"]["location"]:
        if location["locationName"] == city:
            weather = location["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            return f"{city} 天氣：{weather}"
    
    return "請輸入正確的城市名稱"

# LINE Webhook 入口
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return "OK"

# 訊息處理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    city = event.message.text  # 使用者輸入的城市名稱
    weather_info = get_weather(city)
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather_info))

# 啟動 Flask 伺服器
if __name__ == "__main__":
    app.run(port=5000)

    pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add requirements.txt"
git push origin main

