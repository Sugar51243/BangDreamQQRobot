from ncatbot.core import BotClient, GroupMessage, MessageChain
from command.bangdream.src.function.chart.tools import addFuzzyKey, userInputToKey
from functions.randomData import randomDetermination
from functions.requestData import requestData
import command.bangdream.src.function.chart.char as char
import command.bangdream.src.function.card.card as card
import command.bangdream.src.function.player_info.playerInfo as playerInfo
import command.bangdream.src.function.user_Binding.userBinding as userBinding
import functions.sendMessage as sendMessage
import re


async def handle_group(bot: BotClient, msg: GroupMessage, raw_message: str, be_at: bool, owner: list):
    
    #查自制谱
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "自制":
        charID = inputed_Command[1].strip()
        withMP3 = False
        if command[-3:] == "带音乐":
            charID = charID[:-3]
            withMP3 = True
        if len(inputed_Command) <= 1:
            message = MessageChain(["参数缺失,可用参数:\n"])
            message += MessageChain(["[ID]\n"])
            await sendMessage.replyMsgToGroup(bot=bot,msg=msg, messageChain=message)
            return
        await char.sreachSelfMakeChart(bot, msg, charID, withMP3)
        return
    #查官谱
    if raw_message[0:2] == "官谱":
        command = raw_message[2:].strip()
        if len(command) <= 0:
            message = MessageChain(["参数缺失,可用参数:\n"])
            message += MessageChain(["[ID/歌名/关键词 难度]\n"])
            await sendMessage.replyMsgToGroup(bot=bot,msg=msg, messageChain=message)
            return
        inputed_Command = command.split(" ")
        d = inputed_Command[-1]
        [no_d_input, d] = userInputToKey(d)
        #update charID
        if no_d_input == False:
            command = command[:-2].strip()
        await char.sreachOfficalMakeChart(bot, msg, command, d)
        return
    #查谱
    if raw_message[0:2] == "查谱":
        command = raw_message[2:].strip()
        if len(command) <= 0:
            message = MessageChain(["\n参数缺失,可用参数:\n"])
            message += MessageChain(["-------------------------\n"])
            message += MessageChain(["[歌名/关键词/ID 难度]\n"])
            message += MessageChain(["例:六兆年 sp\n"])
            message += MessageChain(["-------------------------\n"])
            message += MessageChain(["[(等级/乐团名称/歌曲种类) 难度]\n"])
            message += MessageChain(["例:萝 lv27 翻唱 hd\n"])
            message += MessageChain(["-------------------------\n"])
            message += MessageChain(["注意事项:\n"])
            message += MessageChain(["1. 搜索将以歌名搜索优先\n"])
            message += MessageChain(["2. 等级搜索请在前加上lv\n例: lv41\n"])
            message += MessageChain(["3. 难度并非过滤器参数\n"])
            message += MessageChain(["4. 此功能为搜谱，并非搜曲\n"])
            message += MessageChain(["-------------------------\n"])
            message += MessageChain(["搜索结果将被限制于10首以内，超出数量的情况请使用茨菇，而非使用小生物"])
            await sendMessage.replyMsgToGroup(bot=bot,msg=msg, messageChain=message)
            return
        try:
            charID = command
            withMP3 = False
            if command[-3:] == "带音乐":
                charID = charID[:-3]
                withMP3 = True
            #try to check it as 自制
            url = "https://bestdori.com/api/post/details?id=" + charID
            data = requestData(url)
            chartDetail = data["post"]["chart"]
            #if it is not a chart, a key error will happen here
            await char.sreachSelfMakeChart(bot, msg, charID, withMP3)
            return
        except:
            #try to check it as 官谱
            inputed_Command = command.split(" ")
            d = inputed_Command[-1]
            [no_d_input, d] = userInputToKey(d)
            #update charID
            if no_d_input == False:
                charID = command[:-2].strip()
            await char.sreachOfficalMakeChart(bot, msg, charID, d)
            return
    #随机查谱
    if raw_message == "随机查谱":
        await char.randomSreachChart(bot, msg)
        return
    # handling complex command
    if '查卡' in raw_message and "947" in raw_message:
        if str(msg.sender.user_id) in owner:
            if randomDetermination(50):
                await card.sreachCard(bot, msg, 947)
                return
        message = MessageChain([" 不许查!!!"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    # hanlding command 查卡
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "查卡":
        cardID = inputed_Command[1].strip()
        await card.sreachCard(bot, msg, cardID)
        return
    # hanlding command 随机查卡
    if raw_message == "随机查卡":
        await card.randomSreachCard(bot, msg)
        return
    # hanlding command 随机卡面
    if raw_message == "随机卡面":
        await card.randomGetCard(bot, msg)
        return
    # hanlding command 查玩家
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "查玩家":
        playerID = inputed_Command[1].strip()
        server = "cn"
        if len(inputed_Command) >= 3:
            server = inputed_Command[2].strip()
        await playerInfo.sreachPlayer(bot, msg, playerID, server)
        return
    # handling command 绑定记录
    if raw_message[0:3] == "查绑定":
        await userBinding.checkUserBinded(bot, msg)
        return
    # hanlding command 删除绑定
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "删除绑定":
        inputed_BindID = re.findall(r'(\d+)', raw_message)
        if len(inputed_BindID>0):
            bindID = int(inputed_BindID[0])
            bindID -= 1
        await userBinding.delUserBinded(bot, msg, bindID)
        return
    # hanlding command 绑定玩家
    inputed_Command = re.findall(r'(\D+|\d+)', raw_message)
    if inputed_Command[0] == "绑定":
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
    # hanlding command 新增搜索词
    if raw_message[:5] == "新增搜索词":
        command = raw_message[5:].strip()
        id = re.findall(r'(\d+)', command)[0]
        command = command.replace(id,"").strip()
        command = command.replace("，",",")
        sreachKey = []
        keySet = command.split(",")
        for key in keySet:
            sreachKey.append(key.strip())
        addFuzzyKey(id= id, keySet= sreachKey)
        message = MessageChain([f" 已为谱面ID [{id}] 新增关键词 {sreachKey} "])
        await sendMessage.replyMsgToGroup(bot, msg, message)
    
