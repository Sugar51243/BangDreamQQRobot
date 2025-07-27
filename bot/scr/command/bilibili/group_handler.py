from ncatbot.core import BotClient, GroupMessage, MessageChain, Video
import urllib, json, httpx
import functions.sendMessage as sendMessage

#QQ小程序签名认证以获取短分享网址
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

#error code
bvErrorCode = -1

#资料卡转换至短分享网址
def cardToUrl(card: dict):
    clean_url = json.loads(card["data"]["data"])["meta"]["detail_1"]["qqdocurl"]
    clean_url = str(clean_url).split("?")[0]
    return clean_url

#短分享网址转换至长分享网址
def shortUrlToBvUrl(shortUrl: str):
    req = urllib.request.Request(shortUrl, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        bv_url = response.geturl()
    return bv_url

#长分享网址转换至BV号
def pickBvFromLongUrl(longUrl: str):
    bv = str(longUrl).replace("https://www.bilibili.com/video/", "").split("/")[0]
    return bv

#资料卡转换至BV号
def cardToBv(card: dict):
    #pick up the share url -> short: https://b23.tv/...
    clean_url = cardToUrl(card)
    print(f"[I][Bilibili Video Handler]: Video share link get: [{clean_url}]")
    #request with full video link
    bv_url = shortUrlToBvUrl(clean_url)
    #pick up bvid from link
    bv = pickBvFromLongUrl(bv_url)
    return bv

#取得可获取的最高视频画质
def getHighestQuality(bv: int | str):
    bv = str(bv)
    url = f"https://api.nxvav.cn/api/bilivideo/?bv={bv}&p=1&otype=json"
    response = httpx.get(url)
    accept_quality = json.loads(response.text)["accept_quality"]
    print(f"[I][Bilibili Video Handler]: Accept Quality: [{accept_quality}]")
    return accept_quality[0]

#取得视频源
def getVideoLink(bv: int | str, quality):
    url = f"https://api.nxvav.cn/api/bilivideo/?bv={bv}&p=1&q={quality}&format=mp4&otype=url"
    response = httpx.get(url)
    url = response.text
    print(f"[I][Bilibili Video Handler]: Video url: [{url}]")
    return url

#BV号转换至视频源
def bvToVideoUrl(bv: int | str):
    bv = str(bv)
    accept_quality = getHighestQuality(bv)
    url = getVideoLink(bv, accept_quality)
    return url


#转换bilibili视频分享至视频源
#basic on api : nxvav.cn
async def handle_group(bot: BotClient, msg: GroupMessage, raw_message: str):
    bv = bvErrorCode#error code
    #分辨分享源并取得BV号
    #快捷分享 (资料卡)
    if "[CQ:json,data=" in raw_message and "哔哩哔哩" in raw_message:
        #取得资料卡
        data = msg.message
        shareCard = [card for card in data if card["type"] == "json"][0]
        #转换至BV号
        bv = cardToBv(shareCard)
    #长分享网址(带BV号)
    elif "https://www.bilibili.com/video/" in raw_message:
        #定位网址
        idx = raw_message.find("https://www.bilibili.com/video/")
        #直接从网址中取得BV号
        #不需要完整网址，仅处理前面部分
        bv = pickBvFromLongUrl(raw_message[idx:])
    #短分享网址(不带BV号)
    elif "https://b23.tv/" in raw_message:
        #定位网址并取得完整网址
        idx = raw_message.find("https://b23.tv/")
        url = raw_message[idx:].split(" ")[0]
        #转换至长分享网址
        bv_url = shortUrlToBvUrl(url)
        #直接从网址中取得BV号
        bv = pickBvFromLongUrl(bv_url)
    #检查BV号获取状况
    if bv == bvErrorCode:
        return
    #转换至视频源
    print(f"[I][Bilibili Video Handler]: Video BV get: [{bv}]")
    url = bvToVideoUrl(bv)
    #构造信息链并发送
    message = MessageChain([Video(url)])
    await sendMessage.sendMsgToGroup(bot=bot, msg=msg, message=message)
    print(f"[I][Bilibili Video Handler]: Complete Handling Request From User [{msg.sender.user_id}]")




