from ncatbot.core import MessageChain, Image
from command.bangdream.plugin.bestdori.render import render
from command.bangdream.src.dict.pathInfo import charImageStoringPath, keysetPath
from functions.fileHandler import readJson, writeJson

#用户输入|难度参数 字典
userInputKey = {"ez":"easy", "nm":"normal", "hd":"hard", "ex":"expert", "sp":"special"}

#规范化谱面信息
def normalize(charData: list):
    chart = [] #暂存谱面
    #遍历谱面内容
    #此处无视并删除歌曲信息，即歌曲文件名称
    #更改格式，合并绿条种类至一种
    for beat in charData:
        #BPM种类(谱面设定)
        if beat["type"]=="BPM":
            chart.append({"bpm":beat["bpm"],"beat":beat["beat"],"type":"BPM"})
        #单键 -> 包括: 蓝键 & 粉键
        elif beat["type"] == "Single":
            chart.append(beat)
        #正常绿条 -> 需要更改成: 滑动绿条
        elif beat["type"] == "Long":
            chart.append({"type":"Slide","connections":beat["connections"]})
        #滑动绿条
        elif beat["type"] == "Slide":
            chart.append(beat)
        #滑键
        elif beat["type"] == "Directional":
            chart.append(beat)
    #返回谱面
    return chart

#从谱面取得BPM信息
def getBPM(charData: list):
    bpm = [0,0] #暂存BPM信息
    #遍历谱面内容
    for key in charData:
        try:
            #无用bpm数据
            if key["bpm"] <= 0:
                continue
            #如未记录首轮bpm，更新
            if bpm == [0,0]:
                bpm = [key["bpm"], key["bpm"]]
            #如录录得新最低数BPM，更新
            if key["bpm"] < bpm[0]:
                bpm[0] = key["bpm"]
            #如录录得新最高数BPM，更新
            elif key["bpm"] > bpm[1]:
                bpm[1] = key["bpm"]
        except:
            pass
    #返回BPM信息
    return bpm

#从谱面取得物量信息
def countItems(charData: list):
    items = 0 #暂存物量信息
    #遍历谱面内容
    for key in charData:
        try:
            #单键+1
            if key["type"] == "Single" or key["type"] == "Directional":
                items+=1
            #绿条获得所有非隐藏节点并增加
            elif key["type"] == "Slide":
                for data in key["connections"]:
                    try:
                        if data["hidden"] == True:
                            pass
                        else:
                            items+=1
                    except:
                        items+=1
        except:
            pass
    #返回物量信息
    return items

#字典释义: 用户输入 → 完整难度参数
def userInputToKey(difficult: str):
    out:list [bool, str] = [True, "expert"]
    try:
        out[1] = userInputKey[difficult]
        out[0] = False
    except:
        pass
    return out

#字典释义: 难度参数 → 数字参数
def difficultToKey(difficult: str):
    if difficult == "easy":
        difficult = "0"
    elif difficult == "normal":
        difficult = "1"
    elif difficult == "hard":
        difficult = "2"
    elif difficult == "expert":
        difficult = "3"
    elif difficult == "special":
        difficult = "4"
    return difficult

#字典释义: 数字参数 → 难度参数
def keyToDifficult(key: str | int):
    key = str(key)
    if key == "0":
        difficult = "easy"
    elif key == "1":
        difficult = "normal"
    elif key == "2":
        difficult = "hard"
    elif key == "3":
        difficult = "expert"
    elif key == "4":
        difficult = "special"
    return difficult

#谱面渲染至图片
def renderingChart(charData: list, charID: str | int, server: str, difficult = "expert"):
    #渲染
    image = render(charData)
    #文件名称: -> charID | charID-difficult, png format
    if server == "Bandori":
        imageURL: str = f"{charImageStoringPath}{charID}-{difficult}.png"
    else:
        imageURL: str = f"{charImageStoringPath}{charID}.png"
    #储存文件
    image.save(imageURL)
    #返回文件地址
    return imageURL

#查询可用名称
#次序为: 日→陆→台→英→韩
def getName(NameList: list):
    name: str = None
    for idx in [0,3,2,1,4]:
        if NameList[idx]!=None:
                name: str = str(NameList[idx])
                break
    return name

#处理信息
#谱面名称 | 谱面ID | 谱面难度 | 谱面等级 | 谱面 | BPM | 物量 | 时长 | 服务器 | 持有者 | 点赞数
def formMsg(chartData: dict):
    #取出数据
    name = chartData["name"]
    id = chartData["id"]
    difficult = chartData["difficult"].upper()
    level = chartData["level"]
    if chartData["bpm"][0] == chartData["bpm"][1]:
        bpm = f"{chartData["bpm"][0]}"
    else:
        bpm = f"{chartData["bpm"][0]}-{chartData["bpm"][1]}"
    count = chartData["count"]
    time = chartData["time"]
    server = chartData["server"]
    owner = chartData["owner"]
    like = chartData["like"]
    chart = chartData["chart"]
    #构造信息链
    message = MessageChain(["\n"])
    message += MessageChain(["谱面信息\n"])
    message += MessageChain(["--------------------\n"])
    #基础信息
    #谱面名称
    message += MessageChain(["谱面名称:" + name + "\n"])
    #谱面ID
    message += MessageChain(["谱面ID:" + id + "\n"])
    #点赞数
    if server == "Bestdori":
        message += MessageChain(["点赞数:" + like + "\n"])
    #一级信息 ( 谱面难度 | 谱面等级 | 所属乐团或谱师 )
    message += MessageChain(["--------------------\n"])
    #谱面难度
    message += MessageChain(["谱面难度:" + difficult + "\n"])
    #谱面等级
    message += MessageChain(["谱面等级:" + level + "\n"])
    #所属乐团或谱师
    if server == "Bandori":
        message += MessageChain(["所属乐团:" + owner[0] + "\n"])
        message += MessageChain(["乐团分类:" + owner[1] + "\n"])
    else:
        message += MessageChain(["谱师:" + owner + "\n"])
    #二级信息 ( BPM | 物量 | 时长 )
    message += MessageChain(["--------------------\n"])
    #BPM
    message += MessageChain(["BPM:" + bpm + "\n"])
    #物量
    message += MessageChain(["物量:" + count + "\n"])
    #时长
    message += MessageChain(["时长:" + time + "\n"])
    #三级信息 ( 服务器 | 游玩网址 )
    message += MessageChain(["--------------------\n"])
    #服务器
    message += MessageChain(["服务器:" + server + "\n"])
    #游玩网址
    if server == "Bestdori":
        url = f"https://sonolus.bestdori.com/community/levels/bestdori-community-{id}"
        message += MessageChain(["前去游玩:" + url + "\n"])
    #四级信息 ( 谱面图片 )
    message += MessageChain(["--------------------\n"])
    imageURL = renderingChart(charData= chart, charID= id, server= server, difficult= difficult)
    message += MessageChain([Image(imageURL)])
    #返回信息
    return message

#关键词搜索
#支持模糊搜索
def fuzzySearch(keyword: int | str):
    result: list = [] #暂存ID列表
    keyword = str(keyword)
    #读入关键词本
    sreachKey = readJson(path=keysetPath)
    #取出对应记录
    for key in sreachKey:
        if keyword.lower() in key.lower():
            result.extend(sreachKey[key])
    return result

#新增关键词
def addFuzzyKey(id: int | str, keySet: list[str]):
    id = str(id)
    #读入关键词本
    sreachKey = readJson(path=keysetPath)
    #更新
    for key in keySet:
        if key in sreachKey:
            newdata = sreachKey[key].append(id)
            sreachKey.update({key:newdata})
        else:
            sreachKey.update({key:[id]})
    #写入关键词本
    writeJson(path=keysetPath, data=sreachKey)
