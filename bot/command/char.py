from ncatbot.core import MessageChain, Image
import sendMessage
from bestdorix.render import render
from requestData import fileIO_handler

from requestData.request_from_api import requestData


# sreach song id from keyset
def sreachKey(data, codeID):
    try:
        sreachKey = fileIO_handler.readDataFrom(fileIO_handler.sreachingKeyPath)
        codeID = sreachKey[codeID]
        return codeID
    except Exception as e:
        print("Unsuss Sreach of key "+codeID)
        print(e)
        codeID = codeID
        
    for key in data:
        titles = data[key]['musicTitle']
        for title in titles:
            if title == codeID:
                codeID = key
                return codeID
    return "-1"

#Normalize
def normalize(charData):
    chart = []
    for beat in charData:
        if beat["type"]=="BPM":
            chart.append({"bpm":beat["bpm"],"beat":beat["beat"],"type":"BPM"})
        elif beat["type"] == "Single":
            chart.append(beat)
        elif beat["type"] == "Long":
            chart.append({"type":"Slide","connections":beat["connections"]})
        elif beat["type"] == "Slide":
            chart.append(beat)
        elif beat["type"] == "Directional":
            chart.append(beat)
    return chart


#查自制谱
async def sreachSelfMakeChart(bot, msg, charID):
    message = MessageChain(["\n"])
    try:
        url = "https://bestdori.com/api/post/details?id=" + charID
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    try:
        chartDetail = data["post"]["chart"]
    except:
        message = MessageChain(["该贴文并非谱面"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    message += MessageChain(["谱面信息\n"])
    message += MessageChain(["谱面ID:" + charID + "\n"])
    
    #谱面名称
    try:
        message += MessageChain(["谱面名称:" + data["post"]["title"] + "\n"])
    except:
        message += MessageChain(["谱面名称:谱面名称信息搜索失败" + "\n"])
    
    #BPM
    try:
        bpm = data['post']['chart'][0]['bpm']
        message += MessageChain(["BPM:" + str(bpm) + "\n"])
    except:
        message += MessageChain(["BPM:BPM信息搜索失败" + "\n"])
    
    #物量
    try:
        items = data['post']['content'][2]['data']
        message += MessageChain([str(items) + "\n"])
    except:
        message += MessageChain(["物量:物量信息搜索失败" + "\n"])
    
    #时长
    try:
        time = data['post']['content'][4]['data']
        message += MessageChain([time + "\n"])
    except:
        message += MessageChain(["时长:时长信息搜索失败" + "\n"])
    
    #谱师
    try:
        author = data['post']['author']["username"]
        message += MessageChain(["谱师:" + author + "\n"])
    except:
        message += MessageChain(["谱师:谱师信息搜索失败" + "\n"])
    
    #点赞数
    try:
        likes = data['post']["likes"]
        message += MessageChain(["点赞数:" + str(likes) + "\n"])
    except:
        message += MessageChain(["点赞数:点赞数信息搜索失败" + "\n"])
    
    message += MessageChain(["服务器:" + "Bestdori社区自制谱" + "\n"])
    message += MessageChain(["前去游玩:" + "https://sonolus.bestdori.com/community/levels/bestdori-community-"+ charID + "\n"])
    
    try:
        image = render(data["post"]["chart"])
        imageURL = fileIO_handler.ChartImageSavingPath +charID+".png"
        image.save(imageURL)
        message += MessageChain([Image(imageURL)])
    except:
        message += MessageChain(["谱面加载失败" + "\n"])
    
    await sendMessage.replyMsgToGroup(bot, msg, message)

#查官谱
async def sreachOfficalMakeChart(bot, msg, charID, d):
    message = MessageChain(["\n"])
    try:
        try:
            url = "https://bestdori.com//api/songs/all.1.json"
            data = requestData(url)
        except:
            message = MessageChain(["服务器网络连接出错"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
        songData = data[charID]
    except:
        message = MessageChain(["输入并非歌曲ID，正在尝试歌名搜索"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        
        try:
            url = "https://bestdori.com//api/songs/all.1.json"
            data = requestData(url)
        except:
            message = MessageChain(["服务器网络连接出错"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
        charID = sreachKey(data, charID)
        if charID=="-1":
            message = MessageChain(["搜索失败，无相应关键词"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
    
    try:
        url = f"https://bestdori.com/api/charts/{charID}/{d}.json"
        data = requestData(url)
    except:
        message = MessageChain(["歌曲不存在"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    chart = normalize(data)
    
    message += MessageChain(["谱面信息\n"])
    message += MessageChain(["谱面ID:" + charID + "\n"])
    message += MessageChain(["谱面难度:" + d + "\n"])
    
    try:
        url = "https://bestdori.com//api/songs/all.7.json"
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    message += MessageChain(["谱面名称: "])
    try:
        message += MessageChain([f"{data[charID]['musicTitle'][0]} ({data[charID]['musicTitle'][3]})\n"])
    except:
        message += MessageChain(["谱面名称信息搜索失败"])
    
    #所属乐团
    message += MessageChain(["所属乐团: "])
    try:
        bandID = data[charID]["bandId"]
        url = "https://bestdori.com//api/bands/main.1.json"
        bands = requestData(url)
        message += MessageChain(f'{bands[str(bandID)]["bandName"][0]} ({bands[str(bandID)]["bandName"][3]})\n')
    except:
        message += MessageChain('其他\n')
    
    if d == "easy":
        d = "0"
    elif d == "normal":
        d = "1"
    elif d == "hard":
        d = "2"
    elif d == "expert":
        d = "3"
    elif d == "special":
        d = "4"
    
    try:
        difficulty = data[charID]['difficulty'][d]['playLevel']
        message += MessageChain("谱面等级:" + str(difficulty) + "\n")
    except:
        raise Exception("谱面等级信息搜索失败")
        
    try:
        bpm = data[charID]['bpm'][d][0]['bpm']
        message += MessageChain(["BPM:" + str(bpm) + "\n"])
    except:
        message += MessageChain(["BPM:BPM信息搜索失败" + "\n"])
    
    try:
        items = data[charID]['notes'][d]
        message += MessageChain(["物量:" + str(items) + "\n"])
    except:
        message += MessageChain(["物量:物量信息搜索失败" + "\n"])
    
    try:
        time = data[charID]['length']
        message += MessageChain(["时长:" + str(time) + "\n"])
    except:
        message += MessageChain(["时长:时长信息搜索失败" + "\n"])
    
    message += MessageChain(["服务器:Bandori" + "\n"])
    
    try:
        image = render(chart)
        imageURL = fileIO_handler.ChartImageSavingPath+charID+"-"+d+".png"
        image.save(imageURL)
        message += MessageChain([Image(imageURL)])
    except:
        message += MessageChain(["谱面加载失败" + "\n"])
    
    await sendMessage.replyMsgToGroup(bot, msg, message)