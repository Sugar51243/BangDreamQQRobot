from ncatbot.core import MessageChain

import sendMessage
from playerInfo import *

import requestData.fileIO_handler as fileIO_handler


#绑定记录
async def checkUserBinded(bot, msg):
    message = MessageChain(["\n"])
    try:
        message += MessageChain(["绑定记录:\n"])
        users = fileIO_handler.readDataFrom(fileIO_handler.userBindingPath)
        user = users[str(msg.sender.user_id)]
        for i in range(len(user)):
            message += MessageChain([f"{i+1}. {i['acc']} {i['server']}\n"])
    except:
        message += MessageChain(["无绑定记录"])
    await sendMessage.replyMsgToGroup(bot, msg, message)

#删除绑定
async def delUserBinded(bot, msg, bindID = 0):
    message = MessageChain(["\n"])
    try:
        users = fileIO_handler.readDataFrom(fileIO_handler.userBindingPath)
        user = users[str(msg.sender.user_id)]
        del user[bindID]
        users.update({str(msg.sender.user_id):user})
        fileIO_handler.writeDatainFile(fileIO_handler.userBindingPath, users)
        message += MessageChain(["账号删除成功"])
    except:
        message += MessageChain(["无绑定记录"])
    await sendMessage.replyMsgToGroup(bot, msg, message)

#绑定玩家
async def bindPlayer(bot, msg, playerID, server="cn"):
    
    data = await getPlayer(bot, msg, playerID, server)
    if data == {}:
        return
    
    users = fileIO_handler.readDataFrom(fileIO_handler.userBindingPath)
    if users == {}:
        message = MessageChain(["服务器文件处理出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    try:
        data = users[str(msg.sender.user_id)]
    except:
        data = []
    
    for savedData in data:
        if playerID == savedData["acc"] and server == savedData["server"]:
            message = MessageChain(["请求重复, 账号已储存"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
    
    data.append({"acc":playerID, "server": server})
    users.update({str(msg.sender.user_id):data})
    
    fileIO_handler.writeDatainFile(fileIO_handler.userBindingPath, users)
    
    message = MessageChain(["账号储存成功"])
    await sendMessage.replyMsgToGroup(bot, msg, message)
    
    await checkUserBinded(msg)

#玩家状态
async def playerInfo(bot, msg, listID):
    users = fileIO_handler.readDataFrom(fileIO_handler.userBindingPath)
    try:
        user = users[str(msg.sender.user_id)][listID]
    except:
        message = MessageChain(["无绑定记录"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    await sreachPlayer(bot, msg, user["acc"], user["server"])