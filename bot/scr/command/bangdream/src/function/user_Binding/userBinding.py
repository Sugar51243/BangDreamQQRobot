from ncatbot.core import MessageChain
import functions.sendMessage as sendMessage
from command.bangdream.src.function.player_info.playerInfo import getUser, sreachPlayer
from functions.fileHandler import readJson, writeJson
from command.bangdream.src.dict.pathInfo import userBindingPath

#绑定记录
async def checkUserBinded(bot, msg):
    message = MessageChain(["\n"])
    try:
        message += MessageChain(["绑定记录:\n"])
        users = readJson(path=userBindingPath)
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
        users = readJson(path=userBindingPath)
        user = users[str(msg.sender.user_id)]
        del user[bindID]
        users.update({str(msg.sender.user_id):user})
        writeJson(path=userBindingPath, data=users)
        message += MessageChain(["账号删除成功"])
    except:
        message += MessageChain(["无绑定记录"])
    await sendMessage.replyMsgToGroup(bot, msg, message)

#绑定玩家
async def bindPlayer(bot, msg, playerID, server="cn"):
    #检查用户存在
    data = await getUser(bot, msg, playerID, server)
    if data == {}:
        return
    #读取文件
    users = readJson(path=userBindingPath)
    try:
        data = users[str(msg.sender.user_id)]
    except:
        data = []
    #检查数据未绑定
    for savedData in data:
        if playerID == savedData["acc"] and server == savedData["server"]:
            message = MessageChain(["请求重复, 账号已储存"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
    #更新
    data.append({"acc":playerID, "server": server})
    users.update({str(msg.sender.user_id):data})
    #写入文件
    writeJson(path=userBindingPath, data=users)
    #反馈
    message = MessageChain(["账号储存成功"])
    await sendMessage.replyMsgToGroup(bot, msg, message)
    await checkUserBinded(msg)

#玩家状态
async def playerInfo(bot, msg, listID):
    #读取玩家绑定记录
    users = readJson(path=userBindingPath)
    try:
        user = users[str(msg.sender.user_id)][listID]
    except:
        message = MessageChain(["无绑定记录"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #查玩家资料
    await sreachPlayer(bot, msg, user["acc"], user["server"])