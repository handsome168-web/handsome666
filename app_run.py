from __future__ import unicode_literals
import os
import redis
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from urllib.request import urlopen
import configparser
from linebot.models import *
import re

redis1 = redis.Redis(host = "redis-13333.c56.east-us.azure.cloud.redislabs.com", password = "ubZLeDUxIKCYKBHK15dtY3TjfnmPw824", port = "13333")
redis1.set("symptoms","Fever,Cough,Shortness of breath or difficulty breathing,Tiredness,Aches,Runny nose and Sore throat.")
redis1.set("protection","1,clean your hands for at least 20 seconds with soap and water, or use an alcohol-based sanitiser with at least 70% alcohol.2,cover your sneeze or cough with your elbow or with tissue.3,avoid close contact with people who are ill.4,avoid touching your eyes, nose and mouth.")
redis1.set("risk factors","1,Recent travel from or residence in an area with ongoing community spread of COVID-19 as determined by CDC or WHO.2,Close contact with someone who has COVID-19 — such as when a family member or health care worker takes care of an infected person.")

# from custom_models import ChannelTalks #, ChannelFlex, utils

app = Flask(__name__)

# get LINE tokens from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


# Obtain LINE information
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# repeat text message
@handler.add(MessageEvent, message=TextMessage)
# import redis
# list out all reply options:
def reply_text_message(event):
    print(event)
    text = event.message.text
    text = text.strip()
    try:
        if (re.findall("symptom",text,re.I)[0] != None):
            reply_text = redis1.get("symptoms").decode('UTF-8')
    except:
        try:
            if (re.findall("(protection)",text,re.I)[0] != None or re.findall("(precaution)",text,re.I)[0] != None):
                reply_text = redis1.get("protection").decode('UTF-8') 
        except:
            try:
                if (re.findall("(risk factors)",text,re.I)[0] != None):
                    reply_text = redis1.get("risk factors").decode('UTF-8')  
            except:
                reply_text = text
    if (event.source.user_id != "Udeadbeefdfeadfsdlkfdasofjewa"):
        reply = False #not yet replied

        #trying reply by condition:
        if not reply:
            reply = ChannelTalks.location_search(event)
        #***
        #To add other reply options
        #***
        #finally, if not get replied yet:
    message = TextSendMessage(reply_text)
    line_bot_api.reply_message(event.reply_token, message)

# if __name__ == "__main__":
#     app.run()

if __name__ == "__main__":
    heroku_port = os.getenv('PORT', None)
    app.run(host='0.0.0.0', port=heroku_port)
