import os
import re
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入 .env 環境變數
load_dotenv()

app = Flask(__name__)

# LINE BOT 憑證
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 中央氣象局 API KEY
CWB_API_KEY = os.getenv("CWB_API_KEY")

# 所有支援的城市對照表（別名 → 正式名稱）
city_alias = {
    '台北': '臺北市', '台北市': '臺北市', '臺北': '臺北市', '臺北市': '臺北市',
    '新北': '新北市', '新北市': '新北市', '台北縣': '新北市',
    '基隆': '基隆市', '基隆市': '基隆市',
    '桃園': '桃園市', '桃園市': '桃園市',
    '新竹': '新竹市', '新竹市': '新竹市', '新竹縣': '新竹縣',
    '台中': '臺中市', '台中市': '臺中市', '臺中': '臺中市', '臺中市': '臺中市',
    '苗栗': '苗栗縣', '苗栗縣': '苗栗縣',
    '彰化': '彰化縣', '彰化縣': '彰化縣',
    '南投': '南投縣', '南投縣': '南投縣',
    '雲林': '雲林縣', '雲林縣': '雲林縣',
    '嘉義': '嘉義市', '嘉義市': '嘉義市', '嘉義縣': '嘉義縣',
    '台南': '臺南市', '台南市': '臺南市', '臺南': '臺南市', '臺南市': '臺南市',
    '高雄': '高雄市', '高雄市': '高雄市',
    '屏東': '屏東縣', '屏東縣': '屏東縣',
    '台東': '臺東縣', '台東縣': '臺東縣', '臺東': '臺東縣', '臺東縣': '臺東縣',
    '花蓮': '花蓮縣', '花蓮縣': '花蓮縣',
    '宜蘭': '宜蘭縣', '宜蘭縣': '宜蘭縣',
    '澎湖': '澎湖縣', '澎湖縣': '澎湖縣',
    '金門': '金門縣', '金門縣': '金門縣',
    '連江': '連江縣', '連江縣': '連江縣',
}

def normalize_city(user_input):
    """嘗試比對城市名稱（模糊比對）"""
    for key in city_alias:
        if key in user_input:
            return city_alias[key]
    return None

def get_weather(city_name):
    """從中央氣象局 API 取得天氣資料"""
    endpoint = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": city_name,
        "format": "JSON"
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            location_data = data["records"]["location"][0]
            city = location_data["locationName"]
            weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            min_temp = location_data["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
            max_temp = location_data["weatherElement"][4]["time"][0]["parameter"]["parameterName"]

            return (f"{city} 今天天氣：{weather}\n"
                    f"降雨機率：{rain}%\n"
                    f"氣溫：{min_temp}°C - {max_temp}°C")
        except Exception:
            return "解析天氣資料時發生錯誤，請稍後再試。"
    else:
        return "無法取得天氣資訊，請確認城市名稱是否正確。"

@app.route("/callback", methods=['POST'])
def callback():
    # 驗證 LINE 簽名
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    normalized = normalize_city(user_msg)
    if normalized:
        weather_info = get_weather(normalized)
        reply = weather_info
    else:
        reply = ("歡迎使用天氣小幫手!🌤️\n"
                 "我可以協助查詢台灣各縣市的即時天氣！\n"
                 "請輸入: XX市 或 XX縣 進行查詢 🐰\n"
                 "例如：台北市、臺中市")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
