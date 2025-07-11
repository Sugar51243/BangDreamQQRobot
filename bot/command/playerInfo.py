from ncatbot.core import MessageChain
import sendMessage

from requestData.request_from_api import requestData

allowedServers = ["jp", "cn", "tw", "en", "kr"]

#check server input vaild
def checkServerAble(server):
    for allowedServer in allowedServers:
        if server == allowedServer:
            return True
    return False

#Get user data from bestdori server
async def getUser(bot, msg, playerID, server):
    
    if checkServerAble(server) == False:
        message = MessageChain(["服务器参数错误"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    
    try:
        url = f"https://bestdori.com/api/player/{server}/{playerID}"
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    
    if data['data']['profile'] == None:
        message = MessageChain(["玩家不存在"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return {}
    
    return data

#查玩家
async def sreachPlayer(bot, msg, playerID, server):
    message = MessageChain(["\n"])
    data = await getUser(bot, msg, playerID, server)
    if data == {} : return

    try:
        userName = data['data']['profile']['userName']
        message += MessageChain([f"用户名称: {userName}"+ "\n"])
    except:
        message += MessageChain(["用户名称: 获取失败\n"])
            
    try:
        rank = data['data']['profile']['rank']
        message += MessageChain(["用户等级: " + str(rank) + "\n"])
    except:
        message += MessageChain(["用户等级: 获取失败" + "\n"])
    
    message += MessageChain(["用户ID: " + str(playerID) + "\n"])
    
    try:
        introduction = data['data']['profile']['introduction']
        message += MessageChain(["账号简介:\n" + introduction + "\n"])
    except:
        message += MessageChain(["账号简介: 获取失败" + "\n"])
    
    message += MessageChain(["----------"+"\n"])
    message += MessageChain(["通关状况"+"\n"])
    try:
        esayC = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['clearedMusicCount']
        esayFC = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['fullComboMusicCount']
        esayAP = data['data']['profile']['userMusicClearInfoMap']['entries']['easy']['allPerfectMusicCount']
        
        normalC = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['clearedMusicCount']
        normalFC = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['fullComboMusicCount']
        normalAP = data['data']['profile']['userMusicClearInfoMap']['entries']['normal']['allPerfectMusicCount']
        
        hardC = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['clearedMusicCount']
        hardFC = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['fullComboMusicCount']
        hardAP = data['data']['profile']['userMusicClearInfoMap']['entries']['hard']['allPerfectMusicCount']
        
        expertC = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['clearedMusicCount']
        expertFC = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['fullComboMusicCount']
        expertAP = data['data']['profile']['userMusicClearInfoMap']['entries']['expert']['allPerfectMusicCount']
        
        specialC = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['clearedMusicCount']
        specialFC = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['fullComboMusicCount']
        specialAP = data['data']['profile']['userMusicClearInfoMap']['entries']['special']['allPerfectMusicCount']
        
        message += MessageChain(["EASY"+"\n"])
        message += MessageChain(["通关:"+str(esayC)+"   "+"全连:"+str(esayFC)+"   "+"AP:"+str(esayAP)+"\n"])
                    
        message += MessageChain(["NORMAL"+"\n"])
        message += MessageChain(["通关:"+str(normalC)+"   "+"全连:"+str(normalFC)+"   "+"AP:"+str(normalAP)+"\n"])
        
        message += MessageChain(["HARD"+"\n"])
        message += MessageChain(["通关:"+str(hardC)+"   "+"全连:"+str(hardFC)+"   "+"AP:"+str(hardAP)+"\n"])
        
        message += MessageChain(["EXPERT"+"\n"])
        message += MessageChain(["通关:"+str(expertC)+"   "+"全连:"+str(expertFC)+"   "+"AP:"+str(expertAP)+"\n"])
        
        message += MessageChain(["SPECIAL"+"\n"])
        message += MessageChain(["通关:"+str(specialC)+"   "+"全连:"+str(specialFC)+"   "+"AP:"+str(specialAP)+"\n"])
    
    except:
        message += MessageChain(["获取失败" + "\n"])
    
    await sendMessage.replyMsgToGroup(bot, msg, message)