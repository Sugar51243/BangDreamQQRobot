import io, os, json, random, requests
from PIL import Image
from datetime import datetime
from ncatbot.core import MessageChain, At, Reply
import functions.sendMessage as sendMessage
from functions.fileHandler import readJson, writeJson


gameList = {}
gameInfoPath = "command/ygo/data/gameInfo.json"
deckPath = "command/ygo/data"

#Both
#-------------------------------------------------------------
#tools
#-------------------------------------------------------------
#tools -> 取得未缴交卡组的参赛者
def returnNoDeckPlayer(gameName: str):
    #已缴交卡组的参赛者列表
    submited = returnHaveDeckPlayer(gameName)
    #从数据文件取得参赛者列表
    loaded_data = readJson(gameInfoPath)
    game_data = loaded_data[gameName]
    gamerList = game_data["member"]
    #筛选
    result = [gamer for gamer in gamerList if gamer not in submited]
    return result

#tools -> 查询已缴交卡组列表
def returnHaveDeckPlayer(gameName: str):
    #查询已缴交卡组列表
    path = f"{deckPath}/{gameName}"
    deckList = os.listdir(path)
    #已缴交卡组的参赛者列表
    submited = [int(deckInfo.split(".")[0]) for deckInfo in deckList]
    return submited

#tools -> 发送信息
async def sendMsg(bot, msg, message):
    try:
        await sendMessage.replyMsgToGroup(bot, msg, message)
    except:
        await sendMessage.sendMsgToPrivate(bot, msg, message)



#Befor Start
#-------------------------------------------------------------
#tools
#-------------------------------------------------------------
#tools -> 返回文字信息
#游戏名称 | 申请群号 | 举办者QQ号 | 工作人员列表 | 服务器地址 | 服务器名称 | 开始时间 | 奖品 | 参赛名单 | 
async def returnInfo(bot, gameName=None, game_data=None):
    #从数据文件取得必要信息
    loaded_data = readJson(gameInfoPath)
    #游戏名称
    try:
        if gameName == None:
            gameName = game_data["name"]
        game_data = loaded_data[gameName]
    except:
        return "比赛不存在"
    name = gameName
    #申请群号
    group_id = game_data["from"]
    #举办者QQ号
    osg_info = await bot.api.get_user_card(user_id=game_data["osg"])
    #举办者名称
    osg_name = json.loads(osg_info['data']['arkMsg'])['meta']['contact']['nickname']
    #工作人员列表
    stuffs = []
    for user_id in game_data["stuff"]:
        user_info = await bot.api.get_user_card(user_id)
        user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
        stuffs.append(user_name)
    #服务器地址
    server_url = game_data["server"]['url']
    #服务器名称
    server_name = game_data["server"]['name']
    #开始时间
    start_time = game_data['start']
    #奖品
    awards = game_data['award']
    #参赛名单
    member = []
    for user_id in game_data['member']:
        user_info = await bot.api.get_user_card(user_id)
        user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
        member.append(user_name)
    #处理数据
    text = f"群赛名称: {name}\n"
    text += f"所属群组: {group_id}\n"
    text += f"举办者: {osg_name}\n"
    text += "工作人员:\n"
    i = 1
    for user in stuffs:
        text += f"{i}. {user}\n"
        i+=1
    text += "--------------------\n"
    text += f"服务器: {server_url} ({server_name})\n"
    text += f"开始时间: {start_time}\n"
    text += "奖品:\n"
    for rank in awards:
        text += f"{rank}: {awards[rank]}\n"
    if len(awards) <= 0:
        text += "无\n"
    text += "--------------------\n"
    text += "参赛名单:\n"
    i = 1
    for user_name in member:
        text += f"{i}. {user_name}\n"
        i+=1
    if len(member) <= 0:
        text += "无\n"
    text += "--------------------\n"
    text += "卡组未提交:\n"
    un_submite_players = returnNoDeckPlayer(gameName=gameName)
    i = 1
    for member in un_submite_players:
        user_info = await bot.api.get_user_card(member)
        user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
        text += f"{i}. {user_name}\n"
        i += 1
    if i == 1:
        text += "无\n"
    return text

#tools -> 检测比赛状态
async def checkStartOrNot(bot, msg, gameName):    
    for game in gameList:
        data = gameList[game]
        if data["name"] == gameName:
            message = MessageChain([f"比赛于{game}进行中"])
            sendMsg(bot, msg, message)
            return True
    return False

#tools -> 检测用户权限
async def checkP(bot, msg, gameName, user_id):
    loaded_data = readJson(gameInfoPath)
    try:
        game_data = loaded_data[gameName]
        stuffs = game_data["stuff"]
        if msg.sender.user_id not in stuffs:
            message = MessageChain(["无权限"])
            sendMsg(bot, msg, message)
            message = MessageChain(["仅工作人员有操作权限"])
            sendMsg(bot, msg, message)
            message = MessageChain(["名单如下:\n"])
            i = 1
            for user in stuffs:
                message += MessageChain([f"{i}. {user}\n"])
                i+=1
            sendMsg(bot, msg, message)
            return False
        return True
    except:
        message = MessageChain(["比赛不存在"])
        sendMsg(bot, msg, message)
        return False


#-------------------------------------------------------------
#For OSG | Stuff
#-------------------------------------------------------------
#创建群赛 <- in Group √
async def addNewGame(bot, msg, gameName, start_time, server_url="mygo.superpre.pro:888", server_name='萌卡超先行'):
    #查重
    try:
        data = loaded_data[gameName]
        message = MessageChain(["比赛已存在"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    except:
        pass
    #参数读取
    #申请群号
    group_id = str(msg.group_id) #can't change
    #游戏名称
    name = gameName              #change able
    #举办者QQ号
    osg = msg.sender.user_id
    #工作人员列表
    stuff = [osg,]
    #服务器
    server_data = {"name":server_name, "url":server_url}
    #开始时间
    start_time = start_time
    #奖品
    award = {}
    #参赛名单
    member = []
    #创建字典记录 (对象)
    game_data = {"from": group_id, "osg": osg, "stuff": stuff, "server": server_data, "start": start_time, "award": award, "member": member}
    data = {name:game_data}
    #更新
    loaded_data = readJson(gameInfoPath) #读取文件
    loaded_data.update(data)
    writeJson(gameInfoPath, loaded_data)
    #创建比赛文件夹 -> 卡组储存
    newpath = f"{deckPath}/{gameName}"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    #反馈
    text = "\n游戏创建完成，以下为相关信息:\n"
    text += await returnInfo(bot, gameName=gameName)
    text += "\n\n"
    text += f"PS: 查询赛程输入'比赛信息 {gameName}'"
    message = MessageChain([text])
    await sendMessage.replyMsgToGroup(bot, msg, message)

#删除群赛 <- in Group √ | Private √
async def delGame(bot, msg, gameName):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #更新
    loaded_data = readJson(gameInfoPath)#读取文件
    del loaded_data[gameName]
    writeJson(gameInfoPath, loaded_data)
    #反馈
    message = MessageChain(["比赛已删除"])
    sendMsg(bot, msg, message)

#更改群赛名称 <- in Group √ | Private √
async def changeGameName(bot, msg, gameName, newName):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #更新
    loaded_data = readJson(gameInfoPath)#读取文件
    game = loaded_data[gameName]
    del loaded_data[gameName]
    loaded_data.update({newName:game})
    writeJson(gameInfoPath, loaded_data)
    #反馈
    message = MessageChain(["比赛名称已更新"])
    sendMsg(bot, msg, message)

#新增工作人员权限 <- in Group √ | Private √
async def addStuff(bot, msg, gameName, newStuff):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #更新
    loaded_data = readJson(gameInfoPath)#读取文件
    game_data = loaded_data[gameName]
    stuffs = game_data["stuff"]
    if newStuff not in stuffs:
        stuffs.append(newStuff)
        game_data.update({"stuff":stuffs})
        loaded_data.update({gameName:game_data})
        writeJson(gameInfoPath, loaded_data)
        message = MessageChain(["工作人员名单已更新"])
        sendMsg(bot, msg, message)
        return
    #反馈
    message = MessageChain(["该用户已有工作人员权限"])
    sendMsg(bot, msg, message)

#更改服务器信息 <- in Group √ | Private √
async def changeServer(bot, msg, gameName, server_url, server_name):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #更新
    loaded_data = readJson(gameInfoPath)#读取文件
    game_data = loaded_data[gameName]
    game_data.update({"server":{"url": server_url, "name": server_name}})
    loaded_data.update({gameName:game_data})
    writeJson(gameInfoPath, loaded_data)
    #反馈
    message = MessageChain(["服务器信息已更新"])
    sendMsg(bot, msg, message)

#更改奖品信息 <- in Group √ | Private √
async def addAward(bot, msg, gameName, rank, award):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #更新
    loaded_data = readJson(gameInfoPath)#读取文件
    game_data = loaded_data[gameName]
    awards = game_data["award"]
    awards.update({rank:award})
    game_data.update({"award":awards})
    loaded_data.update({gameName:game_data})
    writeJson(gameInfoPath, loaded_data)
    #反馈
    message = MessageChain(["奖品信息已更新"])
    sendMsg(bot, msg, message)

#注册卡组图片至后台(需人工审卡组) <- in Private √
async def submitDeck(bot, msg, gameName, image_url, gamer_id=None):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #读取参数
    if gamer_id==None:
        gamer_id = msg.sender.user_id
    #拉取/下载 图片
    img = Image.open(requests.get(image_url, stream=True).raw)
    newpath = f"{deckPath}/{gameName}/{gamer_id}.png"
    img.save(newpath)
    #反馈
    message = MessageChain(["已储存"])
    await sendMessage.sendMsgToPrivate(bot, msg, message)


#-------------------------------------------------------------
#For Player
#-------------------------------------------------------------
#参赛 <- in Group √ | Private √
async def joinGame(bot, msg, gameName, gamer_id=None):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
            return
    #读取参数
    if gamer_id == None:
        gamer_id = msg.sender.user_id
    #从数据文件取得必要信息
    loaded_data = readJson(gameInfoPath)
    try:
        game_data = loaded_data[gameName]
    except:
        message = MessageChain(["比赛不存在"])
        sendMsg(bot, msg, message)
        return
    #参赛名单
    member = game_data["member"]
    #查重
    if gamer_id not in member:
        member.append(gamer_id)
    #更新
    game_data.update({"member":member})
    loaded_data.update({gameName:game_data})
    writeJson(gameInfoPath, loaded_data)
    #游戏已启动 则 同步更新 至 暂存记录
    try:
        game = gameList[str(msg.group_id)]
        member = game["member"]
        member.append(gamer_id)
        game_data.update({"member":member})
        gameList.update({str(msg.group_id):game})
    except:
        pass
    #反馈
    message = MessageChain(["已参赛"])
    sendMsg(bot, msg, message)


#-------------------------------------------------------------
#For Both
#-------------------------------------------------------------
#发送比赛信息 <- in Group √ | Private √
async def checkGame(bot, msg, gameName):
    text = "" 
    if await checkStartOrNot(bot, msg, gameName):
        for game in gameList:
            if gameList[game] == gameName:
                text = await returnInfo(bot, game_data=gameList[game])
                break
    else:
        text = await returnInfo(bot, gameName=gameName)
    message = MessageChain(["\n" + text])
    sendMsg(bot, msg, message)


#After Start
#tools
#-------------------------------------------------------------
#tools -> 检测卡组缴交状态，并自动退赛
async def checkDeckSub(bot, msg, gameName):
    submited = returnHaveDeckPlayer(gameName)
    non_submited = returnNoDeckPlayer(gameName)
    for member in non_submited:
        user_info = await bot.api.get_user_card(member)
        user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
        message = MessageChain([f"{user_name}未提交卡组，已退赛"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
    return submited

#tools -> 检测此轮游戏是否完结
async def checkRoundEnded(bot, msg, pairList):
    for pair in pairList:
        if len(pair) != 1 and len(pair) != 3:
            message = MessageChain([f"{pair[0]}与{pair[1]}比赛未完成"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return False
    return True


#-------------------------------------------------------------
#For OSG | Stuff
#-------------------------------------------------------------
#开始比赛 <- in Group √
async def startGame(bot, msg, gameName):
    #查询比赛状态
    if await checkStartOrNot(bot, msg, gameName):
        return
    if await checkP(bot, msg, gameName, msg.sender.user_id) == False:
        return
    #从数据文件取得必要信息
    loaded_data = readJson(gameInfoPath)
    game_data = loaded_data[gameName]
    #查重
    try:
        group_id = str(msg.group_id)
        data = gameList[group_id]
        message = MessageChain(["群内已有比赛进行中"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #将记录登录于暂存中
    except:
        try:
            game_data["round"]
            game_data["name"]
        except:
            gamerList = await checkDeckSub(bot, msg, gameName)
            game_data.update({"member": gamerList})
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            game_data.update({"start": time})
            game_data.update({"name": gameName})
            game_data.update({"round": {"0":[]}})
        gameList.update({group_id:game_data})
        loaded_data.update({gameName:game_data})
        writeJson(gameInfoPath, loaded_data)
        message = MessageChain(["比赛已开始"])
        await sendMessage.replyMsgToGroup(bot, msg, message)

#配对参赛者，并分房 <- in Group √
async def pairPlayer(bot, msg):
    message = MessageChain([f"\n"])
    #查询比赛状态
    try:
        game_data = gameList[str(msg.group_id)]
        stuffs = game_data["stuff"]
        if msg.sender.user_id not in stuffs:
            raise Exception()
    except:
        message = MessageChain(["比赛未开始或无权限"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    if await checkRoundEnded(bot, msg, game_data["round"][str(len(game_data["round"])-1)]) == False:
        return
    #仅一位玩家时自动胜利
    if len(game_data["member"])<=1:
        await endGame(bot, msg)
        return
    #配对参赛者
    pair_list = [] #暂存配对
    #取得参赛者列表，并 打乱
    member = game_data["member"]
    member_temp = []
    while len(member) > 0:
        idx = random.randint(0,len(member)-1)
        member_temp.append(member[idx])
        del member[idx]
    member = member_temp.copy()
    #两位随机配对
    while len(member_temp)>0:
        #参赛者轮空
        if len(member_temp) == 1:
            pair_list.append([member_temp[0]])
            break
        #配对
        pair = [] #暂存
        #抽取首位玩家
        idx = random.randint(0,len(member_temp)-1)
        pair.append(member_temp[idx])
        del member_temp[idx]
        #抽取次位玩家
        idx = random.randint(0,len(member_temp)-1)
        pair.append(member_temp[idx])
        del member_temp[idx]
        #更新暂存配对
        pair_list.append(pair)
    #更新数据
    #开启新一轮 并 记录配对数据
    thisRound = str(len(game_data["round"]))
    game_data["round"].update({thisRound:pair_list})
    game_data.update({"member":member})
    #更新
    loaded_data = readJson(gameInfoPath)
    loaded_data.update({game_data["name"]:game_data})
    writeJson(gameInfoPath, loaded_data)
    #反馈
    #比赛名
    message += MessageChain([f"比赛名: {game_data['name']}\n"])
    #举办者信息
    osg_info = await bot.api.get_user_card(user_id=game_data["osg"])
    osg_name = json.loads(osg_info['data']['arkMsg'])['meta']['contact']['nickname']
    message += MessageChain([f"举办者信息: {osg_name}\n"])
    #服务器
    message += MessageChain([f"服务器: {game_data['server']['url']} ({game_data['server']['name']})\n"])
    #分组时间
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message += MessageChain([f"分组时间: {time}\n"])
    message += MessageChain(["---------------\n"])
    #奖品
    awards = game_data["award"]
    message += MessageChain(["奖品:\n"])
    for rank in awards:
        message += MessageChain([f"{rank}: {awards[rank]}\n"])
    if len(awards) <= 0:
        message += MessageChain(["无\n"])
    message += MessageChain(["--------------------\n"])
    #该轮配对信息
    message += MessageChain([f"Round {int(thisRound)}\n"])
    message += MessageChain(["---------------\n"])
    i = 1
    for group in pair_list:
        try:
            user_info_1 = await bot.api.get_user_card(user_id=group[0])
            user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
            user_info_2 = await bot.api.get_user_card(user_id=group[1])
            user_name_2 = json.loads(user_info_2['data']['arkMsg'])['meta']['contact']['nickname']
            message += MessageChain([f"Group {i}\n"])
            message += MessageChain([f"{user_name_1} vs {user_name_2}\n"])
            message += MessageChain([f"房间密码: M#{game_data['name']}{i}格\n"])
            message += MessageChain(["\n"])
        except:
            user_info_1 = await bot.api.get_user_card(user_id=group[0])
            user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
            message += MessageChain([f"{user_name_1} 轮空\n"])
            message += MessageChain(["\n"])
        i+=1
    message += MessageChain(["\n"])
    message += MessageChain(["提示: 为各位参赛者体验考虑，请勿随意烧条\n"])
    message += MessageChain(["提示: 如果不介意，请保留比赛录像并发给我\n"])
    await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)

#判负并删除参赛者资料 <- in Group √
async def gamerLose(bot, msg, user_id):
    #查询比赛状态
    try:
        game_data = gameList[str(msg.group_id)]
        stuffs = game_data["stuff"]
        if msg.sender.user_id not in stuffs:
            raise Exception()
    except:
        message = MessageChain(["比赛未开始或无权限"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #记录胜者
    pairList = game_data["round"][str(len(game_data["round"])-1)]
    removed = False
    for pair in pairList:
        if user_id in pair:
            pairTemp = pair.copy()
            pairTemp.remove(user_id)
            pair.append(pairTemp[0])
            removed = True
            break
    game_data["round"].update({str(len(game_data["round"])-1):pairList})
    #更新参赛者 → 删除
    member = game_data["member"]
    if user_id not in member or removed == False:
        user_info_1 = await bot.api.get_user_card(user_id=user_id)
        user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
        message = MessageChain([f"选手{user_name_1}未参赛或已落选"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    else:
        member.remove(user_id)
    game_data.update({"member":member})
    #反馈
    user_info_1 = await bot.api.get_user_card(user_id=user_id)
    user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
    message = MessageChain([f"选手{user_name_1}落选"])
    await sendMessage.replyMsgToGroup(bot, msg, message)
    #更新数据
    loaded_data = readJson(gameInfoPath)
    loaded_data.update({game_data["name"]:game_data})
    writeJson(gameInfoPath, loaded_data)
    #反馈
    if len(member)>1:
        await sendPair(bot, msg)
    elif len(member)<=1:
        await endGame(bot, msg)

#完结或暂停比赛 <- in Group √
async def endGame(bot, msg):
    try:
        game_data = gameList[str(msg.group_id)]
        stuffs = game_data["stuff"]
        if msg.sender.user_id not in stuffs:
            raise Exception()
    except:
        message = MessageChain(["比赛未开始或无权限"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    if len(game_data["member"]) != 1:
        
        loaded_data = readJson(gameInfoPath)
        loaded_data.update({game_data["name"]:game_data})
        writeJson(gameInfoPath, loaded_data)
        
        del gameList[str(msg.group_id)]
        
        message = MessageChain([f"比赛暂停，赛程已储存"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    
    game_data["round"].update({str(len(game_data["round"])):[game_data["member"][0]]})
    
    loaded_data = readJson(gameInfoPath)
    loaded_data.update({game_data["name"]:game_data})
    writeJson(gameInfoPath, loaded_data)
    
    del gameList[str(msg.group_id)]
    
    user_info_1 = await bot.api.get_user_card(user_id=game_data["member"][0])
    user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
    message = MessageChain([f"恭喜{user_name_1}选手胜出比赛，取得第一"])
    await sendMessage.replyMsgToGroup(bot, msg, message)
    
    message = MessageChain([f"如要获取过去比赛小组信息，请输入 '赛程回顾 {game_data['name']}'"])
    await sendMessage.replyMsgToGroup(bot, msg, message)

#-------------------------------------------------------------
#For Both
#-------------------------------------------------------------
#发送参赛名单 <- in Group √
async def sendMember(bot, msg):
    
    try:
        game_data = gameList[str(msg.group_id)]
    except:
        message = MessageChain(["此指令仅在比赛开始后有效"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    member = game_data['member']
    message = MessageChain(["参赛名单:\n"])
    i = 1
    for user_id in member:
        user_info = await bot.api.get_user_card(user_id=user_id)
        user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
        message += MessageChain([f" {i}. {user_name}\n"])
        i+=1
    await sendMessage.replyMsgToGroup(bot, msg, message)

#发送比赛小组状态 <- in Group √
async def sendPair(bot, msg):
    
    try:
        game_data = gameList[str(msg.group_id)]
    except:
        message = MessageChain(["此指令仅在比赛开始后有效"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    pairList = game_data["round"][str(len(game_data["round"])-1)]
    message = MessageChain(["比赛小组状态:\n"])
    i = 1
    for pair in pairList:
        if len(pair) == 1:
            user_info = await bot.api.get_user_card(user_id=pair[0])
            user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
            message += MessageChain([f" Group{i}. {user_name} 轮空\n"])
        elif len(pair) == 3:
            user_info = await bot.api.get_user_card(user_id=pair[2])
            user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
            message += MessageChain([f" Group{i}. {user_name} 胜出\n"])
        elif len(pair) >= 2:
            user_info_1 = await bot.api.get_user_card(user_id=pair[0])
            user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
            user_info_2 = await bot.api.get_user_card(user_id=pair[1])
            user_name_2 = json.loads(user_info_2['data']['arkMsg'])['meta']['contact']['nickname']
            message += MessageChain([f" Group{i}. {user_name_1} vs {user_name_2} 比赛中\n"])
        i+=1
    await sendMessage.replyMsgToGroup(bot, msg, message)

#发送赛程回顾 <- in Group √ | Private √
async def reviewGame(bot, msg, gameGame):
    loaded_data = readJson(gameInfoPath)
    
    try:
        game_data = loaded_data[gameGame]
    except:
        message = MessageChain(["比赛不存在"])
        sendMsg(bot, msg, message)
        return
    
    try:
        roundData = game_data["round"]
    except:
        message = MessageChain(["比赛未开始"])
        sendMsg(bot, msg, message)
        return
    
    message = MessageChain(["\n赛程回顾\n"])
    for key in roundData:
        message += MessageChain(["---------------\n"])
        message += MessageChain([f"Round {int(key)}\n"])
        message += MessageChain(["---------------\n"])
        i = 1
        for pair in roundData[key]:
            if type(pair) == int:
                pair = [pair]
            if len(pair) == 1:
                user_info = await bot.api.get_user_card(user_id=pair[0])
                user_name = json.loads(user_info['data']['arkMsg'])['meta']['contact']['nickname']
                if key == str(len(game_data["round"])-1):
                    message += MessageChain([f" {user_name}取得第一\n"])
                else:
                    message += MessageChain([f" Group{i}. {user_name}轮空\n"])
            elif len(pair) > 1:
                user_info_1 = await bot.api.get_user_card(user_id=pair[0])
                user_name_1 = json.loads(user_info_1['data']['arkMsg'])['meta']['contact']['nickname']
                user_info_2 = await bot.api.get_user_card(user_id=pair[1])
                user_name_2 = json.loads(user_info_2['data']['arkMsg'])['meta']['contact']['nickname']
                winner = await bot.api.get_user_card(user_id=pair[2])
                winner = json.loads(winner['data']['arkMsg'])['meta']['contact']['nickname']
                message += MessageChain([f" Group{i}. {user_name_1} vs {user_name_2}: {winner}胜出\n"])
                i+=1
        message += MessageChain([f"\n"])
    sendMsg(bot, msg, message)