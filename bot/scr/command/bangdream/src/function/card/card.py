from ncatbot.core import MessageChain, Image
import functions.sendMessage as sendMessage, random
from functions.requestData import requestData
from functions.randomData import randomDetermination

#查卡
async def sreachCard(bot, msg, cardID):
    message = MessageChain(["\n"])
    try:
        url = f"https://bestdori.com/api/cards/{cardID}.json"
        data = requestData(url)
    except:
        message = MessageChain(["没有搜索到符合条件的卡牌"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #角色信息
    message += MessageChain(["角色信息\n"])
    message += MessageChain(["--------------------\n"])
    #角色名称
    message += MessageChain(["角色名称: "])
    try:
        characterID = data["characterId"]
        url = f"https://bestdori.com/api/characters/{characterID}.json"
        characters = requestData(url)
        message += MessageChain(f'{characters["characterName"][0]} ({characters["characterName"][3]})\n')
    except:
        message += MessageChain(["获取失败\n"])
    #所处乐团
    message += MessageChain(["所处乐团: "])
    try:
        characterID = data["characterId"]
        url = f"https://bestdori.com/api/characters/{characterID}.json"
        characters = requestData(url)
        url = "https://bestdori.com//api/bands/main.1.json"
        bands = requestData(url)
        message += MessageChain(f'{bands[str(characters["bandId"])]["bandName"][0]} ({bands[str(characters["bandId"])]["bandName"][3]})\n')
    except:
        message += MessageChain(["获取失败\n"])
    #卡片信息
    message += MessageChain(["\n卡片信息\n"])
    message += MessageChain(["--------------------\n"])
    #卡片名称
    message += MessageChain(["卡片名称: "])
    try:
        message += MessageChain(f'{data["prefix"][0]} ({data["prefix"][3]})\n')
    except:
        message += MessageChain(["获取失败\n"])
    #卡片ID
    message += MessageChain(["卡片ID: "])
    try:
        message += MessageChain([str(cardID) + '\n'])
    except:
        message += MessageChain(["获取失败\n"])
    #星级
    message += MessageChain(["星级: "])
    try:
        message += MessageChain(f'{data["rarity"]}\n')
    except:
        message += MessageChain(["获取失败\n"])
    #属性
    message += MessageChain(["属性: "])
    try:
        message += MessageChain(f'{data["attribute"]}\n')
    except:
        message += MessageChain(["获取失败\n"])
    #等级上限
    message += MessageChain(["等级上限: "])
    try:
        message += MessageChain(f'{data["levelLimit"]}\n')
    except:
        message += MessageChain(["获取失败\n"])
    message += MessageChain(["--------------------\n"])
    #技能
    message += MessageChain(["技能\n"])
    message += MessageChain(["--------------------\n"])
    try:
        message += MessageChain(f'{data["skillName"]}\n')
    except:
        message += MessageChain(["获取失败\n"])
    message += MessageChain(["--------------------\n"])
    message += MessageChain(["效果\n"])
    message += MessageChain(["--------------------\n"])
    try:
        skillID = str(data["skillId"])
        url = "https://bestdori.com/api/skills/all.2.json"
        skill = requestData(url)[skillID]
        message += MessageChain(f'{skill["simpleDescription"][0]}\n({skill["simpleDescription"][3]})\n')
    except:
        message += MessageChain(["获取失败\n"])
    message += MessageChain(["--------------------\n"])
    #数据
    message += MessageChain(["数据 \n"])
    message += MessageChain(["--------------------\n"])
    message += MessageChain('Lv1: \n')
    try:
        performance = data["stat"]["1"]["performance"]
        technique = data["stat"]["1"]["technique"]
        visual = data["stat"]["1"]["visual"]
        message += MessageChain(f'performance: {performance}\n')
        message += MessageChain(f'technique: {technique}\n')
        message += MessageChain(f'visual: {visual}\n')
    except:
        message += MessageChain(["获取失败\n"])
    message += MessageChain(["--------------------\n"])
    try:
        performance = data["stat"][str(data["levelLimit"])]["performance"]
        technique = data["stat"][str(data["levelLimit"])]["technique"]
        visual = data["stat"][str(data["levelLimit"])]["visual"]
        try:
            performance += data["stat"]["episodes"][0]["performance"] + data["stat"]["episodes"][1]["performance"]
            technique += data["stat"]["episodes"][0]["technique"] + data["stat"]["episodes"][1]["technique"]
            visual += data["stat"]["episodes"][0]["visual"] + data["stat"]["episodes"][1]["visual"]
            message += MessageChain(f'Lv.{data["levelLimit"]} (Episodes 1&2 clear): \n')
        except:
            message += MessageChain(f'Lv.{data["levelLimit"]}: \n')
        message += MessageChain(f'performance: {performance}\n')
        message += MessageChain(f'technique: {technique}\n')
        message += MessageChain(f'visual: {visual}\n')
    except:
        message += MessageChain(["获取失败\n"])
    #Image
    message = message + Image(getImage(data,False))
    if data['rarity']>=3:
        message = message + Image(getImage(data,True))
    await sendMessage.replyMsgToGroup(bot, msg, message)

#随机查卡
async def randomSreachCard(bot, msg):
    cardID = await randomCardID(bot, msg)
    if cardID == "":
        return
    await sreachCard(bot, msg, cardID)

#随机卡面
async def randomGetCard(bot, msg):
    message = MessageChain(["\n"])
    cardID = await randomCardID(bot, msg)
    if cardID == "":
        return
    try:
        url = f"https://bestdori.com/api/cards/{cardID}.json"
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    train = False
    if data['rarity']>=3:
        train = randomDetermination(49)
    message = message + Image(getImage(data,train))
    await sendMessage.replyMsgToGroup(bot, msg, message)

#随机一个卡面ID
async def randomCardID(bot, msg):
    try:
        url = "https://bestdori.com/api/cards/all.0.json"
        data = requestData(url)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return ""
    index = []
    for key in data:
        index.append(key)
    idx = random.randint(0, len(index)-1)
    return index[idx]

#从bestdori拉取卡面图片
def getImage(data, train):
    res = data['resourceSetName']
    if train:
        image = f"https://bestdori.com/assets/jp/characters/resourceset/{res}_rip/card_after_training.png"
    else:
        image = f"https://bestdori.com/assets/jp/characters/resourceset/{res}_rip/card_normal.png"
    return image

