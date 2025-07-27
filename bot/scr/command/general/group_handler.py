from ncatbot.core import BotClient, GroupMessage, MessageChain, Record, Image
from functions.fileHandler import listFile, readFile, readJson, writeJson
from functions.permission import registrationUpdate
from functions.randomData import randomDetermination
import functions.sendMessage as sendMessage, random, datetime, json
import re

robotAcc = [3260850774, 3968200051, 1437848636]

async def handle_group(bot: BotClient, msg: GroupMessage, raw_message: str, be_at: bool, owner: list):
    #指令种类: 在线测试
    #测试信息
    if raw_message.lower() in ["test", "在线吗", "在吗"]:
        print("[General Group]: 指令[测试信息]获取")
        if str(msg.sender.user_id) in owner:
            message = MessageChain(["我在"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            path = "D:/Learning/Workplaces/TestQQAi/NcatBot-AI/scr/command/general/data/美图/6528DE0A40A3E35AA89DD3AEB87A9672.gif"
            message = MessageChain([Image(path)])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
    #指令种类: 互动
    #身份确认
    if  "你是谁" in raw_message and be_at:
        print("[General Group]: 指令[身份确认]获取")
        MessageList = ["我是人", "不是机器人", "好吧，其实我是机器人", "其实我不是机器人", "是号主上线哒", "你猜？"]
        message = MessageChain([MessageList[random.randint(0, len(MessageList)-1)]])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #发癫文案
    if ("fd" in raw_message.lower() or "发癫" in raw_message) and be_at:
        print("[General Group]: 指令[发癫文案]获取")
        #彩蛋
        if randomDetermination(1):
            print("[General Group]: [发癫文案]彩蛋判定成功(1)...")
            if randomDetermination(1):
                print("[General Group]: [发癫文案]彩蛋判定成功(2)...")
                message = MessageChain(["哈哈，我不发"])
                await sendMessage.replyMsgToGroup(bot=bot, msg=msg, messageChain=message)
                return
        #获取文案
        print(f"[General Group]: [发癫文案]获取文件列表中...")
        adFiles = listFile(path="command/general/data/ad")
        print(f"[General Group]: [发癫文案]正在随机文案...")
        idx = random.randint(0,len(adFiles)-1)
        print(f"[General Group]: [发癫文案]文案随机结果: {idx}/{len(adFiles)-1}")
        #发送
        message = MessageChain([readFile(adFiles[idx])])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #美图
    if ("来点" in raw_message and "图" in raw_message) or ("ldt" in raw_message and be_at):
        print("[General Group]: 指令[美图]获取")
        #获取美图
        print(f"[General Group]: [美图]获取文件列表中...")
        imagesList = listFile(path="command/general/data/美图")
        print(f"[General Group]: [美图]正在随机美图...")
        idx = random.randint(0,len(imagesList)-1)
        print(f"[General Group]: [美图]美图随机结果: {idx}/{len(imagesList)-1}")
        #发送
        message = MessageChain([Image(imagesList[idx])])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #今日老婆
    if raw_message in ["jrlp", "今日老婆"]:
        print("[General Group]: 指令[今日老婆]获取")
        #获取今日日期并查询
        today = str(datetime.date.today())
        print(f"[General Group]: [今日老婆]获取今日老婆数据中...")
        try:
            data = readJson(path="command/general/data/jrlp.json")
            todayData = data[today]
        except:
            print(f"[General Group]: [今日老婆]今日数据未更新，正在重置...")
            todayData = {}
        #从数据中获取该群数据记录
        print(f"[General Group]: [今日老婆]获取今日该群[{msg.group_id}]老婆数据中...")
        try:
            groupData = todayData[str(msg.group_id)]
        except:
            print(f"[General Group]: [今日老婆]今日该群[{msg.group_id}]数据未更新，正在重置...")
            groupData = {}
        #尝试查询该用户配对记录
        print(f"[General Group]: [今日老婆]获取今日该用户[{msg.sender.nickname}]老婆数据中...")
        try:
            jrlp = groupData[str(msg.sender.user_id)]
        except:
            print(f"[General Group]: [今日老婆]今日该用户[{msg.sender.nickname}]未有老婆, 开始配对...")
            print(f"[General Group]: [今日老婆]正在获取群员名单...")
            member_list_data = await bot.api.get_group_member_list(group_id=msg.group_id)
            member_list: list = member_list_data['data']
            #更新可配对群员名单
            member_list = [member_list[i]['user_id'] for i in range(len(member_list)) if (member_list[i]['user_id'] != msg.sender.user_id and str(member_list[i]['user_id']) not in groupData)]
            print(f"[General Group]: [今日老婆]可配对名单为: {str(member_list)}")
            #如果全员已配对 则 返回单身信息
            if len(member_list) <= 0:
                print(f"[General Group]: [今日老婆]全员已配对")
                message = MessageChain(["今天你单身"])
                await sendMessage.replyMsgToGroup(bot, msg, message)
                return
            #开始配对
            print(f"[General Group]: [今日老婆]开始配对...")
            idx = random.randint(0,len(member_list)-1)
            jrlp = member_list[idx]
            print(f"[General Group]: [今日老婆]配对结果为: [{str(jrlp)}]")
            #双方同时更新目录
            groupData.update({str(msg.sender.user_id):jrlp})
            groupData.update({jrlp:str(msg.sender.user_id)})
            #更新群数据记录
            todayData.update({str(msg.group_id):groupData})
            #更新当日记录
            data = {today:todayData}
            #储存
            writeJson(path="command/general/data/jrlp.json",data=data)
        #发送
        info = await bot.api.get_group_member_info(group_id=msg.group_id, user_id=jrlp, no_cache=True)
        name = info['data']['nickname']
        card = info['data']['card']
        avatar = f"https://q1.qlogo.cn/g?b=qq&nk={jrlp}&s=640"
        #发送
        message = MessageChain(["\n"])
        if card!="":
            message += MessageChain([f"你今天的老婆是: {card}"])
        else:
            message += MessageChain([f"你今天的老婆是: {name}"])
        message += MessageChain([Image(avatar)])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #赞我
    if "赞我" in raw_message:
        print("[General Group]: 指令[赞我]获取")
        await bot.api.send_like(user_id=msg.sender.user_id, times=1)
        await bot.api.send_poke(user_id=msg.sender.user_id, group_id=msg.group_id)
        message = MessageChain(["赞了"])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #戳我
    if "戳我" in raw_message:
        print("[General Group]: 指令[戳我]获取")
        await bot.api.send_poke(user_id=msg.sender.user_id, group_id=msg.group_id)
        return
    #唱歌
    if raw_message == "唱歌" and be_at:
        print("[General Group]: 指令[唱歌]获取")
        path = ["壱陀矢.mp3", "约德尔唱法.mp3", "_耳_其_进_行_曲.mp3", "_哦哦哦马内~.mp3", "tujitujidandandantujitujidan.mp3", "熙熙攘攘_哦哦哦马内.mp3", "see_you_again.mp3"]
        idx = random.randint(0,len(path)-1)
        message = MessageChain([Record(f"http://127.0.0.1:8080/command/general/data/sound/{path[idx]}")])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #大东北
    if '大东北' in raw_message:
        print("[General Group]: 指令[唱歌]获取")
        message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/大东北.mp3")])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #忠诚
    if "忠诚" in raw_message:
        print("[General Group]: 指令[唱歌]获取")
        message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/你若三冬.mp3")])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #糖笑
    if "糖笑" in raw_message and be_at:
        print("[General Group]: 指令[唱歌]获取")
        message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/糖笑.mp3")])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #糖哭
    if "糖哭" in raw_message and be_at:
        print("[General Group]: 指令[唱歌]获取")
        message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/爱音唐哭.mp3")])
        await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
        return
    #牢大
    keyword = ["牢大", "man", "see you again"]
    for words in keyword:
        if words in raw_message and be_at:
            print("[General Group]: 指令[唱歌]获取")
            message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/see_you_again.mp3")])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
    #复读
    if (raw_message[0] == "说" and be_at) or (raw_message[:3] == "小号说" and str(msg.sender.user_id) in owner):
        print("[General Group]: 指令[复读]获取")
        text = raw_message[raw_message.find("说")+1:].strip()
        print(f"[General Group]: [复读]复读内容为: [{text}]...")
        if ("我喜欢" in text or "我爱" in text) and str(msg.sender.user_id) not in owner:
            message = MessageChain(["唉，癔症..."])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
        if "咕咕嘎嘎" in text:
            path = ["gugugaga.mp3", "gugugaga1.mp3"]
            idx = random.randint(0,len(path)-1)
            message = MessageChain([Record(f"http://127.0.0.1:8080/command/general/data/sound/{path[idx]}")])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
        elif "灵感菇" in text:
            message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/lingangulguli.mp3")])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
        elif "tujitujidandandantujitujidan" in text:
            message = MessageChain([Record("http://127.0.0.1:8080/command/general/data/sound/tujitujidandandantujitujidan.mp3")])
            await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)
            return
        else:
            message = MessageChain([text])
            await sendMessage.sendMsgToGroup(bot, msg, message)
            return
    #指令种类: 实用
    #随机数
    if raw_message[:3].lower() == ".rd":
        print("[General Group]: 指令[随机数]获取")
        #获取参数
        command = raw_message.replace("D","d")
        command = command[3:].strip().lower().split("d")
        command = [command[0]] + re.findall(r'(\d+)', command[1])
        try:
            print(f"[General Group]: [随机数]参数1 : {int(float(command[0]))}")
            print(f"[General Group]: [随机数]参数2 : {int(float(command[1]))}")
            print(f"[General Group]: [随机数]参数3 : {int(float(command[2]))}")
            print(f"[General Group]: [随机数]参数4 : {int(float(command[3]))}")
        except:
            pass
        #次数
        times = 1
        if len(command) >= 4:
            times = int(float(command[3]))
        #构造信息链并投随机数
        message = MessageChain([f"\n"])
        success = 0
        for x in range(times):
            try:
                output = random.randint(int(float(command[0])), int(float(command[1])))
                message += MessageChain([f"{x+1}. {int(float(command[0]))}D{int(float(command[1]))}: {output}"])
                #判定
                if len(command)>=3:
                    message += MessageChain([f" ([>{int(float(command[2]))}]:{"成功" if output>int(float(command[2])) else "失败"})\n"])
                    if output>int(float(command[2])): success += 1
            except:
                message = MessageChain([f"随机数出错"])
        #决定
        idx = raw_message.find("决定我")
        if idx != -1 and len(command) >= 3:
            needToDo = raw_message[idx+3:]
            if needToDo[:3] == "要不要" or needToDo[:2] == "是否": needToDo = needToDo[2:]
            message += MessageChain([f"如果让我决定你是否{needToDo}, 那答案将会是: {"做" if success>=(times/2) else "不做"}"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #注册功能
    if raw_message[:4] == "注册功能" or raw_message[:4] == "功能注册" and be_at:
        print("[General Group]: 指令[注册功能]获取")
        command = raw_message[4:].strip()
        print(f"[General Group]: [注册功能]正常尝试注册功能: [{command}]")
        try:
            if command == "1" or command.lower() == "bangdream" or command.lower() == "bang dream":
                message = registrationUpdate(msg.group_id,"bangdream")
            elif command == "2" or command.lower() == "ygo" or command.lower() == "游戏王":
                message = registrationUpdate(msg.group_id, "ygo")
            elif command == "3" or command.lower() == "bilibili" or command.lower() == "哔哩哔哩":
                message = registrationUpdate(msg.group_id, "bilibili")
            else:
                print(f"[General Group]: [注册功能][{command}]并非可选功能模式")
                raise Exception()
        except:
            message = MessageChain([f"\n功能注册失败或参数错误\n"])
            message += MessageChain([f"可用参数:\n[bangdream, ygo]"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #bug反馈
    if be_at and msg.group_id != 980803820:
        send = False
        for keyword in ["bug", "反馈", "为什么不", "建議"]:
            if keyword in raw_message:
                send = True
                break
        if raw_message == "群号":
            send = True
        if send:
            message = MessageChain("\n号主拉了个群，群号:\n980803820\n有bug或者建議可以进群反馈哦~")
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
    #
    if be_at and msg.sender.user_id not in robotAcc and ("后藤二里" not in msg.sender.nickname and "号机" not in msg.sender.nickname):
        info = await bot.api.get_group_member_info(group_id= msg.group_id ,user_id=msg.sender.user_id, no_cache=True)
        if info["data"]["is_robot"] == True:
            return
        message = MessageChain("怎么了吗？")
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    