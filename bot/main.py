# ========= 导入必要模块 ==========
from ncatbot.core import BotClient, GroupMessage, PrivateMessage, MessageChain
from ncatbot.utils import get_log


import random
import re

import sys
sys.path.append('command')
from playerInfo import sreachPlayer
from card import sreachCard
from card import randomSreachCard
from card import randomGetCard
import char
import sendMessage as sendMessage
import userBinding as userBinding
sys.path.append('command/requestData')
import fileIO_handler as fileIO_handler


# ========== 机器人权限注册 ==========
owner = "1145141919810" #input your own qq acc here

# ========== 创建 BotClient ==========
bot = BotClient()
_log = get_log()

# ========= 注册回调函数 ==========
@bot.group_event()
async def on_group_message(msg: GroupMessage):
    
    _log.info(msg)
    
    await handlingCommand(bot, msg)
    
    command = msg.raw_message.split(" ")
    if command[0] == "add":
        if msg.sender.user_id != int(owner):
            return
        keys = command[1]
        songid = command[2]
        try:
            sreachKey = fileIO_handler.readDataFrom(fileIO_handler.sreachingKeyPath)
            keySet = keys.split("，")
            for key in keySet:
                sreachKey.update({f"{key}":f"{songid}"})
            
            fileIO_handler.writeDatainFile(fileIO_handler.sreachingKeyPath, sreachKey)
                
            message = MessageChain([str(keySet)+" 储存成功"])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        except Exception as e:
            message += MessageChain([str(e)])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
    
@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)

#Random number
def randomDetermination(target):
    num = random.randint(0, 100)
    if num <= target:
        return True
    return False

#Handling Command / Input
async def handlingCommand(bot, msg):
    
    raw_message = msg.raw_message
    
    # handling Testing message
    match raw_message:
        case "hello":
            message = MessageChain(["Hello World"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
                    
        case "test":
            message = MessageChain(["I am inactive and hello world"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
                    
        case "你是人机吗？":
            message = MessageChain(["我是ROBOT"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
    
    # handling complex command
    if raw_message[0] == '查' and raw_message[1] == '卡' and "947" in msg.raw_message:
        if msg.sender.user_id == owner:
            if randomDetermination(35):
                await sreachCard(947, msg)
                return
        message = MessageChain([" 不许查!!!"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
    
    # handling command 复读
    inputed_Command = raw_message.split(" ")
    if inputed_Command[0] == "说" or inputed_Command[0] == "讲" or inputed_Command[0] == "said" or inputed_Command[0] == "复读":
        message = MessageChain([])
        del inputed_Command[0]
        for i in range(len(inputed_Command)):
            message += MessageChain([inputed_Command[i]])
            if i != len(inputed_Command)-1:
                message += MessageChain([" "])
        if len(inputed_Command) >= 1:
            await sendMessage.sendMsgToGroup(bot, msg, message)
    
    # handling command 绑定记录
    if ("绑定" in raw_message) and ( ("记录" in raw_message) or ("查" in raw_message) ):
        await userBinding.checkUserBinded(bot, msg)
        return
    
    # hanlding command 删除绑定
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if ("删" in inputed_Command[0]) and ( ("绑定" in inputed_Command[0]) or ("玩家" in inputed_Command[0]) ):
        inputed_BindID = re.findall(r'(\d+)', raw_message)
        if len(inputed_BindID>0):
            bindID = int(inputed_BindID[0])
            bindID -= 1
        await userBinding.delUserBinded(bot, msg, bindID)
        return
    
    # hanlding command 绑定玩家
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if ("绑定" in inputed_Command[0]) and ( ("玩家" in inputed_Command[0]) or ("账号" in inputed_Command[0])):
        playerID = inputed_Command[1]
        server = "cn"
        if len(inputed_Command) >= 3:
            server = inputed_Command[2]
        await userBinding.bindPlayer(bot, msg, playerID, server)
        return
    
    # hanlding command 玩家状态
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "玩家状态":
        listID = 0
        if len(inputed_Command) >= 2:
            listID == int(inputed_Command[1])-1
        await userBinding.playerInfo(bot, msg, listID)
        return
    
    # hanlding command 查玩家
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "查玩家" or inputed_Command[0] == "玩家":
        playerID = inputed_Command[1]
        server = "cn"
        if len(inputed_Command) >= 3:
            server = inputed_Command[2]
        await sreachPlayer(bot, msg, playerID, server)
        return
    
    # hanlding command 查卡
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "查卡面" or inputed_Command[0] == "查卡" or inputed_Command[0] == "卡面":
        cardID = inputed_Command[1]
        await sreachCard(bot, msg, cardID)
        return
    
    # hanlding command 随机查卡
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "随机查卡":
        await randomSreachCard(bot, msg)
        return
    
    # hanlding command 随机卡面
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "随机卡面":
        await randomGetCard(bot, msg)
        return
    
    #查自制谱
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if "自制" in inputed_Command[0] and "查" in inputed_Command[0]:
        charID = inputed_Command[1]
        await char.sreachSelfMakeChart(bot, msg, charID)
        return
    
    #查官谱
    inputed_Command = raw_message.split(" ")
    if "官" in inputed_Command[0] and "谱" in inputed_Command[0] and "查" in inputed_Command[0]:
        del inputed_Command[0]
        no_d_input = False
        try:
            d = inputed_Command[-1]
            if d == "ez":
                d = "easy"
            elif d == "nm":
                d = "normal"
            elif d == "hd":
                d = "hard"
            elif d == "ex":
                d = "expert"
            elif d == "sp":
                d = "special"
            else:
                no_d_input = True
                d = "expert"
        except:
            no_d_input = True
            d = "expert"
        
        charID = ""
        for i in range(len(inputed_Command)):
            if (i == len(inputed_Command)-1 and no_d_input == False) == True:
                break
            if i != 0:
                charID += " "
            charID += inputed_Command[i]
        await char.sreachOfficalMakeChart(bot, msg, charID, d)
        return
    
    #查谱
    inputed_Command = raw_message.split(" ")
    


# ========== 启动 BotClient==========
if __name__ == "__main__":
    bot.run(enable_webui_interaction=False)

