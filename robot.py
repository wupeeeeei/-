from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
try:
    import xml.etree.cElement as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
line_bot_api=LineBotApi('4olFtAO2hrDmV/PaFkJThCSrzwzDvQlJargX9ST+ZumbYD7L+4nnvhj/hivKT8Iz4azuNahUMKZe/phPzkK5Oyo6O2cPSsCeJneCsq0SOcNiMpYXmfCbtxkFEVd0Di6k2YT/A6ex8Rt4+K1E7w/4oQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('02bbb25a078284ed6c545facde60684a')

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
    mtext = event.message.text
    if mtext == '@本期中獎號碼':
        try:
            message = TextSendMessage(
                text = monoNum(0)
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤! '))
            
    elif mtext == '@前期中獎號碼':
        try:
            message = TextSendMessage(
                text = monoNum(1)+'\n'+monoNum(2)
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '發生錯誤! '))
                                       
    elif len(mtext)==3 and mtext.isdigit():
        try:
            content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
            tree = ET.fromstring(content.text) 
            items = list(tree.iter(tag='item'))
            ptext = items[0][2].text 
            
            ptext = ptext.replace('<p>','').replace('</p','')
            temlist=ptext.split('：')
            prizelist=[]
            prizelist.append(temlist[1][5:8])
            prizelist.append(temlist[2][5:8])
            for i in range(3):
                prizelist.append(temlist[3][9*i+5:9*i+8])
            sixlist=temlist[4].split('、')
           
            for i in range(len(sixlist)):
                prizelist.append(sixlist[i])
            if mtext in prizelist:
                message='符合某獎項後三碼，請自行核對發票前五碼!\n\n'
                message+=monoNum(0)
            else:
                message='很可惜，未中獎，請輸入下一張發票最後三碼。'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(message))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '讀取發票號碼發生錯誤! '))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請輸入發票最後三碼進行對獎!'))

def monoNum(n):
    content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text) 
    items = list(tree.iter(tag='item')) 
    title = items[n][0].text 
    ptext = items[n][2].text 
    ptext = ptext.replace('<p>','').replace('</p','\n')
    return title + '月\n'+ptext[:-1]
if __name__=='__main__':
    app.run()
