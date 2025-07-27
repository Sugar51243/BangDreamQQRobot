import time
from ncatbot.core import MessageChain, BotClient, GroupMessage
import functions.sendMessage as sendMessage
from functions.requestData import requestData

#字典: 可用服务器参数
allowedServers = ["jp", "cn", "tw", "en", "kr"]

def serverToserverID(server: str):
    if server == "jp":
        return 0
    elif server == "cn":
        return 3
    elif server == "tw":
        return 2
    elif server == "en":
        return 1
    elif server == "kr":
        return 4

#从bestdori请求用户资料
async def getUser(bot: BotClient, msg: GroupMessage, playerID: str | int, server: str):
    #检查参数可用
    if server not in allowedServers:
        message = MessageChain(["服务器参数错误"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    #请求用户资料
    try:
        url = f"https://bestdori.com/api/player/{server}/{playerID}?mode=2"
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    #检查用户存在
    if data['data']['profile'] == None:
        message = MessageChain(["玩家不存在"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    return data

#查玩家
#整合,创建并发送信息链
async def sreachPlayer(bot: BotClient, msg: GroupMessage, playerID: str | int, server: str):
    message = MessageChain(["\n"])
    data = await getUser(bot, msg, playerID, server)
    #检查资料
    if data == {} : return
    #用户名称
    try:
        userName = data['data']['profile']['userName']
        message += MessageChain([f"用户名称: {userName}"+ "\n"])
    except:
        message += MessageChain(["用户名称: 获取失败\n"])
    #用户等级
    try:
        rank = data['data']['profile']['rank']
        message += MessageChain(["用户等级: " + str(rank) + "\n"])
    except:
        message += MessageChain(["用户等级: 获取失败" + "\n"])
    #用户ID
    message += MessageChain(["用户ID: " + str(playerID) + "\n"])
    #账号简介
    try:
        introduction = data['data']['profile']['introduction']
        message += MessageChain(["账号简介:\n" + introduction + "\n"])
        message += MessageChain(["--------------------"+"\n"])
    except:
        message += MessageChain(["账号简介: 获取失败" + "\n"])
    #综合力
    areaItems = requestData("https://bestdori.com/api/areaItems/main.5.json")
    userDeckStatus = data['data']["profile"]['mainDeckUserSituations']['entries']
    visual = 0
    technique = 0
    performance = 0
    #计算
    for i in range(5):
        cardStatu = userDeckStatus[i]
        card = cardStatu["userAppendParameter"]["situationId"]
        url = f"https://bestdori.com/api/cards/{card}.json"
        card = requestData(url)
        level = cardStatu["level"]
        #卡面基础值
        tempVisual = int(card["stat"][str(level)]["visual"])
        tempTechnique = int(card["stat"][str(level)]["technique"])
        tempPerformance = int(card["stat"][str(level)]["performance"])
        #用户新增量
        tempVisual += cardStatu["userAppendParameter"]["visual"] + cardStatu["userAppendParameter"]["characterBonusVisual"] + cardStatu["userAppendParameter"]["characterPotentialVisual"]
        tempTechnique += cardStatu["userAppendParameter"]["technique"] + cardStatu["userAppendParameter"]["characterBonusTechnique"] + cardStatu["userAppendParameter"]["characterPotentialTechnique"]
        tempPerformance += cardStatu["userAppendParameter"]["performance"] + cardStatu["userAppendParameter"]["characterBonusPerformance"] + cardStatu["userAppendParameter"]["characterPotentialPerformance"]
        #区域道具
        character = requestData(f"https://bestdori.com/api/characters/{card["characterId"]}.json")
        addVisual = 1
        addTechnique = 1
        addPerformance = 1
        serverID = serverToserverID(server)
        for areaItem in data['data']["profile"]["enabledUserAreaItems"]["entries"]:
            itemID = str(areaItem["areaItemCategory"])
            if character["bandId"] in areaItems[itemID]["targetBandIds"] and card["attribute"] in areaItems[itemID]["targetAttributes"]:
                itemLevel = str(areaItem["level"])
                addVisual += areaItems[itemID]["visual"][itemLevel][serverID]/100
                addTechnique += areaItems[itemID]["technique"][itemLevel][serverID]/100
                addPerformance += areaItems[itemID]["performance"][itemLevel][serverID]/100
        tempVisual *= addVisual
        tempTechnique *= addTechnique
        tempPerformance *= addPerformance
        #
        performance+=tempPerformance
        technique+=tempTechnique
        visual+=tempVisual
    message += MessageChain([f"综合力: {int(performance+technique+visual)}"+"\n"])
    message += MessageChain([f"演出: {int(performance)}"+"\n"])
    message += MessageChain([f"技巧: {int(technique)}"+"\n"])
    message += MessageChain([f"形象: {int(visual)}"+"\n"])
    message += MessageChain(["--------------------"+"\n"])
    #通关状况
    message += MessageChain(["通关状况"+"\n"])
    try:
        #蓝
        esayC = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['clearedMusicCount']
        esayFC = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['fullComboMusicCount']
        esayAP = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['allPerfectMusicCount']
        #绿
        normalC = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['clearedMusicCount']
        normalFC = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['fullComboMusicCount']
        normalAP = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['allPerfectMusicCount']
        #黄
        hardC = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['clearedMusicCount']
        hardFC = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['fullComboMusicCount']
        hardAP = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['allPerfectMusicCount']
        #红
        expertC = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['clearedMusicCount']
        expertFC = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['fullComboMusicCount']
        expertAP = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['allPerfectMusicCount']
        #紫
        specialC = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['clearedMusicCount']
        specialFC = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['fullComboMusicCount']
        specialAP = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['allPerfectMusicCount']
        #创建信息链
        #蓝
        message += MessageChain(["EASY"+"\n"])
        message += MessageChain([f"通关:{esayC}   全连:{esayFC}   AP:{esayAP}\n"])
        message += MessageChain(["--------------------"+"\n"])
        #绿
        message += MessageChain(["NORMAL"+"\n"])
        message += MessageChain([f"通关:{normalC}   全连:{normalFC}   AP:{normalAP}\n"])
        message += MessageChain(["--------------------"+"\n"])
        #黄
        message += MessageChain(["HARD"+"\n"])
        message += MessageChain([f"通关:{hardC}   全连:{hardFC}   AP:{hardAP}\n"])
        message += MessageChain(["--------------------"+"\n"])
        #红
        message += MessageChain(["EXPERT"+"\n"])
        message += MessageChain([f"通关:{expertC}   全连:{expertFC}   AP:{expertAP}\n"])
        message += MessageChain(["--------------------"+"\n"])
        #紫
        message += MessageChain(["SPECIAL"+"\n"])
        message += MessageChain([f"通关:{specialC}   全连:{specialFC}   AP:{specialAP}\n"])
    except:
        message += MessageChain(["获取失败" + "\n"])
    #发送
    await sendMessage.replyMsgToGroup(bot, msg, message)