from ncatbot.core import MessageChain, File
import functions.sendMessage as sendMessage
from command.bangdream.src.function.chart.tools import formMsg, fuzzySearch, keyToDifficult
from command.bangdream.src.function.chart.api import isChart, requestName, requestsChartInfo, returnAllOfficalSong, returnAllOfficalSongKey, sreachByBand, sreachByLevel, sreachByName, sreachByType
from functions.randomData import randomIndex
from command.bangdream.src.dict.pathInfo import songStoringPath


#搜索结果上限
limit = 10

#歌名模式搜索
def sreachFromNameMode(name: str):
    #歌名模式
    #----->歌名
    print(f"[BangDream Handler]: start sreaching by name")
    result = sreachByName(name)
    #----->关键词
    if len(result) < limit:
        print(f"[BangDream Handler]: start fuzzy search")
        result.extend(fuzzySearch(keyword=name))
    return list(set(result))

#条件式搜索
def sreachFromFilterMode(filters: str):
    result = returnAllOfficalSongKey()
    filterResult = []
    resultCount = 0
    #曲目种类
    print(f"[BangDream Handler]: start sreaching by type")
    types = ["原创", "动画", "翻唱", "covers", "cover"]
    for songType in types:
        if songType in filters:
            print(f"[BangDream Handler]: get filter: [type]{songType}")
            filters = filters.replace(songType, "").strip()
            filterResult = sreachByType(songType)
            break
    resultCount+=len(filterResult)
    if len(filterResult)>0:
        result = [song for song in result if song in filterResult]
    #等级
    print(f"[BangDream Handler]: start sreaching by level")
    filterResult = []
    if "lv" in filters:
        command = [lv for lv in filters.split(" ") if "lv" in lv]
        for c in command:
            try:
                level = int(c[2:])
                print(f"[BangDream Handler]: get filter: [level]{level}")
                filters = filters.replace(c, "").strip()
                filterResult = sreachByLevel(level)
                result = [song for song in result if song in filterResult]
                break
            except:
                pass
        if len(filters) == 0: return result
    resultCount+=len(filterResult)
    #乐团名称
    print(f"[BangDream Handler]: start sreaching by band")
    if len(filters) > 0:
        print(f"[BangDream Handler]: get filter: [name]{filters}")
        filterResult = sreachByBand(filters)
        if len(filterResult)>0:
            result = [song for song in result if song in filterResult]
    resultCount+=len(filterResult)
    if resultCount<=0:
        result = []
    return result

#随机查谱
async def randomSreachChart(bot, msg):
    try:
        data = returnAllOfficalSong()
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    id = randomIndex(data)
    song = data[id]
    key = randomIndex(song["difficulty"])
    difficulty = keyToDifficult(key)
    await sreachOfficalMakeChart(bot, msg, id, difficulty)
    return

#查自制谱
async def sreachSelfMakeChart(bot, msg, charID, withMP3: bool):
    print(f"[BangDream Handler]: start sreaching 自制谱 ID: {charID}")
    if (isChart(id=charID, offical=False)) == False:
        return
    try:
        data = requestsChartInfo(offical=False, charID=charID)
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    message = formMsg(data)
    await sendMessage.replyMsgToGroup(bot, msg, message)
    if withMP3:
        path = f"{songStoringPath}{charID}.mp3"
        message = MessageChain([File(path)])
        await sendMessage.replyMsgToGroup(bot, msg, message)

#查官谱
async def sreachOfficalMakeChart(bot, msg, charID: str, d: str):
    #后台信息
    print(f"[BangDream Handler]: start sreaching 官谱 ID: {charID} | 难度: {d}")
    #检查输入是否谱面ID -> 否
    if (isChart(id=charID, offical=True)) == False:
        #后台信息
        message = MessageChain(["检测到输入并非歌曲ID，正在尝试歌名搜索"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        #歌名模式搜索
        result = sreachFromNameMode(name=charID)
        #处理结果
        if len(result) <= 0:
            #后台信息
            message = MessageChain(["歌名搜索失败，正在尝试条件式搜索"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            #条件式搜索
            result = sreachFromFilterMode(filters=charID)
        #后台信息
        print(f"[BangDream Handler]: name sreaching result get: {str(result)}")
        #处理结果
        #如果只有一个结果，即返回谱面信息
        #如果多于一个结果，即返回结果列表
        #如果大于限制，即报错
        if len(result) == 1:
            charID = result[0]
        elif len(result) > limit:
            message = MessageChain([f"\n得到结果为: {len(result)}首\n"])
            message += MessageChain(["--------------------\n"])
            message += MessageChain([f"介于文字发送结果容易占屏刷屏，查询结果受限制至{limit}首\n"])
            message += MessageChain(["--------------------\n"])
            message += MessageChain(["范围过广，请使用其他关键词或使用茨菇查曲"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
        elif len(result) > 1:
            message = MessageChain([f"\n搜索出多项结果({len(result)})，请以ID查询:"])
            data = requestName(result)
            i=0
            for item in data:
                i+=1
                info = data[item]
                message += MessageChain(["\n--------------------\n"])
                message += MessageChain([f"{i}. {info["name"]}\n"])
                message += MessageChain([f"所属乐团: [{info["owner"][0]}]\n"])
                message += MessageChain([f"乐团分类: [{info["owner"][1]}]\n"])
                message += MessageChain([f"等级: {str(info["level"])}\n"])
                message += MessageChain([f"查询: 查谱 {item}"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
        elif len(result) <= 0:
            message = MessageChain(["搜索失败，无该关键字或符合条件的曲目"])
            await sendMessage.replyMsgToGroup(bot, msg, message)
            return
    #处理谱面信息
    try:
        data = requestsChartInfo(offical=True, charID=charID, difficult=d)
    #网络错误
    except:
        message = MessageChain(["服务器网络连接出错"])
        await sendMessage.replyMsgToGroup(bot, msg, message)
        return
    #整合至信息
    message = formMsg(data)
    await sendMessage.replyMsgToGroup(bot, msg, message)