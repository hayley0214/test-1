from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 初始化 LINE Bot API
line_bot_api = LineBotApi('Cyez3SBJqPIV3Jyrf58MzwJAEkVpf+OvcMN1Wv6h0qry8KV0zwSKj6q9neuttVdUu5re7+BorLXfj0rmDIfGvYwQ/kyrd1DTQgNh25XAouoB4nerJ8jSPTB3rQJtsoFeSkAA3PAEAB+lndQEQujRSQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e01ae91e66566f00e45594e223afa0f6')

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers['X-Line-Signature']

    # 獲取請求主體內容
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()
