from ncatbot.core import BotClient, PrivateMessage, MessageChain, Record, Image
import functions.sendMessage as sendMessage, re
import command.ygo.ygo as YGO

async def handle_private(bot: BotClient, msg: PrivateMessage, owner: list):
    raw_message = msg.message
    await bot.api.mark_private_msg_as_read(user_id=msg.sender.user_id)
    
    if raw_message[0]['type'] != "text":
        return
    
    #For Stuff
    #交卡组 gameName (QQ ID) 卡组图片
    command = raw_message[0]['data']['text'].strip()
    if command[:3] == "交卡组":
        if "\n" in command:
            command.replace("\n","")
        message = command[3:].strip()
        #比赛名称
        try:
            gameName = re.findall(r'(\D+)', message)[0].strip()
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #QQ ID
        try:
            gamer_id = int(re.findall(r'(\d+)', message)[0].strip())
        except:
            gamer_id = msg.sender.user_id
        #卡组图片
        try:
            image_url = raw_message[1]['data']['url']
        except:
            message = MessageChain("未检测到卡组图片")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.submitDeck(bot, msg, gameName, image_url, gamer_id)
        return
    
    #删除群赛 比赛名称
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "删除群赛":
        command = command[4:].strip()
        #比赛名称
        try:
            gameName = command
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.delGame(bot, msg, gameName)
        return
    
    #比赛更名 旧比赛名称 新比赛名称
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "比赛更名":
        command = command[4:].strip()
        command_list = command.split(" ")
        #旧比赛名称
        try:
            old_gameName = command_list[0]
        except:
            message = MessageChain("旧比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #新比赛名称
        try:
            new_gameName = command_list[1]
        except:
            message = MessageChain("新比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.changeGameName(bot, msg, old_gameName, new_gameName)
        return
    
    #新增权限 比赛名称 新权限人员(QQ ID)
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "新增权限":
        message = command[4:].strip()
        #比赛名称
        try:
            gameName = re.findall(r'(\D+)', message)[0].strip()
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #QQ ID
        try:
            newStuff = int(raw_message[1]['data']['qq'])
        except:
            input_id = re.findall(r'(\d+)', message)
            if len(input_id) >= 1:
                newStuff = int(input_id[0])
            else:
                message = MessageChain("新权限人员QQ ID参数缺失")
                await sendMessage.sendMsgToPrivate(bot, msg, message)
                return
        #注册到后台
        await YGO.addStuff(bot, msg, gameName, newStuff)
        return
    
    #更改服务器 比赛名称 服务器url 服务器名称
    command = raw_message[0]['data']['text'].strip()
    if command[:5] == "更改服务器":
        message = command[5:].strip()
        data = message.split(" ")
        #比赛名称
        try:
            gameName = data[0]
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        message = message[len(gameName):].strip()
        #服务器名称
        if len(data) < 3:
            message = MessageChain("服务器名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        server_name = data[-1]
        message = message[:-len(server_name)].strip()
        #服务器url
        server_url = message
        if "." not in server_url or ":" not in server_url:
            message = MessageChain("服务器地址参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.changeServer(bot, msg, gameName, server_url, server_name)
        return
    
    #更改奖品 比赛名称 条件 奖品
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "更改奖品":
        message = command[4:].strip()
        data = message.split(" ")
        #比赛名称
        try:
            gameName = data[0]
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #条件
        try:
            rank = data[1]
        except:
            message = MessageChain("条件参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #奖品
        try:
            award = data[2]
        except:
            message = MessageChain("奖品参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.addAward(bot, msg, gameName, rank, award)
        return
    
    
    #For Player
    #参赛 比赛名称 (QQ ID)
    command = raw_message[0]['data']['text'].strip()
    if command[:2] == "参赛":
        
        message = command[2:].strip()
        #比赛名称
        try:
            gameName = re.findall(r'(\D+)', message)[0].strip()
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #QQ ID
        gamer_id = None
        try:
            gamer_id = int(raw_message[1]['data']['qq'])
        except:
            input_id = re.findall(r'(\d+)', message)
            if len(input_id) >= 1:
                gamer_id = int(input_id[0])
        #注册到后台
        await YGO.joinGame(bot, msg, gameName, gamer_id=gamer_id)
        return
    
    
    #For Both
    #比赛信息 比赛名称
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "比赛信息":
        command = command[4:].strip()
        #比赛名称
        try:
            gameName = command
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.checkGame(bot, msg, gameName)
        return
    
    #赛程回顾 比赛名称
    command = raw_message[0]['data']['text'].strip()
    if command[:4] == "赛程回顾":
        message = command[4:].strip()
        #比赛名称
        try:
            gameName = message
        except:
            message = MessageChain("比赛名称参数缺失")
            await sendMessage.sendMsgToPrivate(bot, msg, message)
            return
        #注册到后台
        await YGO.reviewGame(bot, msg, gameName)
        return