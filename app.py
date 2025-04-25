import os
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 中的環境變數

# 讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")


from flask import Flask, request, abort
import os
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 從環境變數讀取 LINE Bot 憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CWB_API_KEY = os.getenv("CWB_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 抓取天氣資料函式
def get_weather(city):
    url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWB_API_KEY}&format=JSON'
    res = requests.get(url)
    data = res.json()

    for location in data['records']['location']:
        if location['locationName'] == city:
            wx = location['weatherElement'][0]['time'][0]['parameter']['parameterName']
            pop = location['weatherElement'][1]['time'][0]['parameter']['parameterName']
            min_t = location['weatherElement'][2]['time'][0]['parameter']['parameterName']
            max_t = location['weatherElement'][4]['time'][0]['parameter']['parameterName']
            return f"{city} 天氣：{wx}\n降雨機率：{pop}%\n氣溫：{min_t}°C ~ {max_t}°C"

    return "請輸入正確的縣市名稱（例如：台北、高雄、台中）"

# Webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# 回覆使用者訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    city = event.message.text.strip()
    result = get_weather(city)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

# 首頁測試用
@app.route('/')
def index():
    return "LINE Bot with CWB Weather is running!"

if __name__ == "__main__":
    app.run()
