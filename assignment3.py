from __future__ import unicode_literals

import os
import sys
import redis

from argparse import ArgumentParser

from flask import Flask, request, abort, jsonify
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text

    if input_text == '@查詢匯率':
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_twd = currency_data['USDTWD']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對台幣 TWD：1:{usd_to_twd}'))








if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
