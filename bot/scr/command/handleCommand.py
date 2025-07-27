from ncatbot.core import BotClient, GroupMessage, PrivateMessage
import re, datetime
from command.permission import returnRegistration
from command.general import group_handler as general_group
from command.bangdream import group_handler as bangdream_group
from command.general.poke_handler import handle_poke
import command.ygo.privateHandler as ygo_private
import command.ygo.groupHandler as ygo_group
import command.bilibili.group_handler as bilibili_group

#正在处理中的用户ID
#单用户仅允许同时处理一个消息
handling_member = []

#机器人名称/简称
robotName = ["盒子里的小生物", "小生物"]

# Tools
#确认信息是否被艾特或回复
#确认指令对象 | 清理艾特信息或回复信息代码
# 返回结构为: [已处理信息 | 艾特状态]
async def msgBeAt(bot: BotClient, msg, robotAcc):
    raw_message = msg.raw_message #信息原数据
    be_at = False #暂存
    #艾特信息
    #结构为: [CQ:at,qq={QQID}]
    if f"[CQ:at,qq={robotAcc}]" in raw_message:
        raw_message = raw_message.replace(f"[CQ:at,qq={robotAcc}]","").strip()
        be_at = True
    #结构为: @{QQID | QQ NickName} | {robotName}
    allowedAt = [f"@{robotAcc}"] #QQID
    allowedAt.extend(robotName) #robotName
    info = await bot.api.get_group_member_info(group_id= msg.group_id ,user_id=robotAcc, no_cache=True)
    allowedAt.append(f"@{info["data"]["nickname"]}") #QQ NickName
    for allowAt in allowedAt:
        if allowAt in raw_message:
            raw_message = raw_message.replace(allowAt,"").strip()
            be_at = True
    #回复信息
    #结构为: [CQ:reply,qq={信息ID}]
    if "[CQ:reply,id=" in raw_message and "]" in raw_message:
        #从结构中取出 信息ID
        relpy_id = re.findall(r'(\d+)', raw_message)[0]
        #取得 信息并确实发送者
        replyed_msg = await bot.api.get_msg(message_id = relpy_id)
        if replyed_msg["data"]["sender"]["user_id"] == int(robotAcc):
            raw_message = raw_message.replace(f"[CQ:reply,id={relpy_id}]","").strip()
            be_at = True
    if len(raw_message)<1:
        raw_message = f"blankmsg,id:{msg.message_id}"
    #返回已处理信息及艾特状态
    return [raw_message, be_at]

#确认信息是否戳戳
#如果信息并非戳戳，sub_type会返回keyError
def isPoke(msg: dict):
    try:
        if msg["sub_type"] != "poke":
            raise Exception()
    except Exception:
        try:
            print(f"[W][Notice Event Handler]: 通知信息并非戳戳")
            print(f"[W][Notice Event Handler]: 通知种类 [{msg["notice_type"]}]")
            print(f"[W][Notice Event Handler]: 通知副种类 [{msg["sub_type"]}]")
        except: pass
        return False
    return True

# 消息处理
#处理群消息
#通用种类 | 邦邦种类 | 游戏王 | 哔哩哔哩
async def handle_group_message(bot: BotClient, robotAcc: int, msg: GroupMessage, owner: list):
    #消息收信时间
    msgTime = datetime.datetime.fromtimestamp(msg.time)
    msgTime = msgTime.strftime(format="%Y-%m-%d %H:%M:%S")
    startTime = datetime.datetime.now()
    startTimeStr = startTime.strftime(format="%Y-%m-%d %H:%M:%S")
    #后台打印信息: 信息处理开始
    print(f"[{startTimeStr}] [Group Message Handler]: 开始处理源[{msg.sender.nickname}](群号:[{msg.group_id}])于[{msgTime}]收信的群消息[{msg.message_id}]")
    #异步锁，阻止重复处理
    if msg.sender.user_id in handling_member:
        print(f"[Group Message Handler]: user [{msg.sender.nickname}] message in handling")
        return
    handling_member.append(msg.sender.user_id)
    #正式处理信息指令
    #处理艾特 | 清理信息
    [raw_message, be_at] = await msgBeAt(bot, msg, robotAcc)
    #取得发送群已注册的指令种类 或 注册基础通用种类功能
    types = returnRegistration(msg.group_id)
    #按种类处理信息
    #通用种类 | 邦邦种类 | 游戏王 | 哔哩哔哩
    for type in types:
        print(f"[Group Message Handler]: 正在尝试以[{type}]模式处理信息[{msg.message_id}]")
        #捕捉异常以防止涵数异常退出 -> 异步锁
        try:
            #通用种类
            if type == "general":
                await general_group.handle_group(bot=bot, msg=msg, raw_message=raw_message, be_at=be_at, owner = owner)
            #邦邦种类
            elif type == "bangdream":
                await bangdream_group.handle_group(bot=bot, msg=msg, raw_message=raw_message, be_at=be_at, owner = owner)
            #游戏王
            elif type == "ygo":
                await ygo_group.handle_group(bot=bot, msg=msg, owner=owner, be_at=be_at)
            #哔哩哔哩
            elif type == "bilibili":
                await bilibili_group.handle_group(bot=bot, msg=msg, raw_message=raw_message)
        #后台打印信息: 异常信息
        except Exception as e:
            print(f"[E][Msg Handler]: {str(e)}")
    #更新异步锁
    handling_member.remove(msg.sender.user_id)
    endTime = datetime.datetime.now()
    endTimeStr = endTime.strftime(format="%Y-%m-%d %H:%M:%S")
    print(f"[{endTimeStr}] [Group Message Handler]: 信息[{msg.message_id}]源[{msg.sender.nickname}](群号:[{msg.group_id}])处理完毕")
    print(f"[{endTimeStr}] [Group Message Handler]: 指令执行时长为: [{endTime-startTime}]")

#处理私信
#游戏王
async def handle_private_message(bot: BotClient, robotAcc: int, msg: PrivateMessage, owner: list):
    #消息收信时间
    msgTime = datetime.datetime.fromtimestamp(msg.time)
    msgTime = msgTime.strftime(format="%Y-%m-%d %H:%M:%S")
    nowTime = datetime.datetime.now()
    nowTime = nowTime.strftime(format="%Y-%m-%d %H:%M:%S")
    #后台打印信息: 信息处理开始
    print(f"[{nowTime}] [Private Message Handler]: [Group Message Handler]: 开始处理源[{msg.sender.nickname}]于[{msgTime}]收信的私信")
    await ygo_private.handle_private(bot=bot, msg=msg, owner=owner)

#处理通知信息
#通用种类 (戳戳)
async def handle_notice_event(bot: BotClient, robotAcc: int, msg: dict, owner: list):
    nowTime = datetime.datetime.now()
    nowTime = nowTime.strftime(format="%Y-%m-%d %H:%M:%S")
    #后台打印信息: 信息处理开始
    group = ""
    try: group = f"(群号:[{msg["group_id"]}])"
    except: pass
    print(f"[{nowTime}] [Notice Event Handler]: 收到源用户ID[{msg["user_id"]}]的通知信息{group}")
    #检查信息种类
    if not isPoke(msg):
        return
    #检查对象
    if msg['target_id'] != int(robotAcc):
        return
    #处理
    await handle_poke(bot=bot, msg=msg, owner=owner)

#
async def handle_request_event(bot: BotClient, robotAcc: int, msg: dict, owner: list):
    pass
