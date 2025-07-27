from functions.requestData import requestData
from functions.fileHandler import writeFile
from command.bangdream.src.function.chart.tools import normalize, difficultToKey, keyToDifficult, getBPM, countItems, getName
from command.bangdream.src.dict.pathInfo import songStoringPath
import eyed3

import requests

#从bestdori请求所有歌曲数据
#原数据
def returnAllOfficalSong():
    song_url = "https://bestdori.com//api/songs/all.7.json"
    data = requestData(song_url)
    return data

#从bestdori请求谱面信息
def requestsChartFromAPI(offical: bool, charID: str | int, difficult="expert"):
    #API整合
    if offical:
        url = f"https://bestdori.com/api/charts/{charID}/{difficult}.json"
    else:
        url = f"https://bestdori.com/api/post/details?id={charID}"
    print(f"[I][bangdream-api-chart]: requested api: {url}")
    #请求
    try:
        data = requestData(url)
    except:
        #请求错误情况 → 网络连接错误 | 网址错误(谱面ID 错误)
        raise KeyError()
    print(f"[I][bangdream-api-chart]: data requested success")
    #规范化
    if offical:
        chart: list = normalize(data)
    else:
        chart: list = data["post"]["chart"]
    print(f"[I][bangdream-api-chart]: chart get and normalize success")
    #返回谱面
    return chart

#从bestdori请求谱面信息
#谱面 | 谱面名称 | 谱面ID | 谱面难度 | 谱面等级 | BPM | 物量 | 时长 | 服务器 | 持有者 | 点赞数
def requestsChartInfo(offical: bool, charID: str | int, difficult="expert"):
    charInfo: dict = {} #暂存谱面信息
    #---->请求谱面
    chart: list = requestsChartFromAPI(offical=offical, charID=charID, difficult=difficult)
    #请求谱面信息
    if offical:
        song_url = "https://bestdori.com//api/songs/all.7.json"
        owner_url = "https://bestdori.com//api/bands/main.1.json"
        song_info = requestData(song_url)[str(charID)]
        owner_info = requestData(owner_url)
    else:
        song_url = f"https://bestdori.com/api/post/details?id={charID}"
        song_info = requestData(song_url)["post"]
    print(f"[I][bangdream-api-chart]: chart info requested success")
    print(f"[I][bangdream-api-chart]: start to process")
    #处理谱面信息
    #---->谱面名称
    if offical:
        name: str = getName(song_info['musicTitle'])
    else:
        name: str = str(song_info["title"])
    #---->谱面ID
    id: str = str(charID)
    #---->谱面难度
    try:
        if offical:
            difficult: str = str(difficult)
        else:
            difficult: str = keyToDifficult(song_info["diff"])
    except:
        difficult: str = "None"
    #---->谱面等级
    try:
        if offical:
            level: str = str(song_info['difficulty'][difficultToKey(difficult)]['playLevel'])
        else:
            level: str = str(song_info["level"])
    except:
        level: str = "None"
    #---->BPM
    try:
        bpm: list | str = getBPM(chart)
    except:
        bpm: list | str = "None"
    #---->物量
    try:
        count: str = str(countItems(chart))
    except:
        count: str = "None"
    #---->时长
    try:
        if offical:
            time: float = float(song_info['length'])
            time: str = f"{time//60:02.0f}:{time%60:02.2f}"
        else:
            audio_url: str = song_info['song']['audio']
            response = requests.get(audio_url)
            path = f"{songStoringPath}{charID}.mp3"
            writeFile(path, response.content)
            duration = eyed3.load(path).info.time_secs
            time: str = f"{duration//60:02.0f}:{duration%60:02.2f}"
    except Exception as e:
        print(e)
        time:str = "None"
    #---->服务器
    if offical:
        server: str = "Bandori"
    else:
        server: str = "Bestdori"
    #---->持有者
    if offical:
        bandID = song_info["bandId"]
        url = "https://bestdori.com//api/bands/main.1.json"
        bands = requestData(url)
        url = "https://bestdori.com//api/bands/all.1.json"
        owner_name = requestData(url)
        if str(bandID) in bands:
            owner: list = [str(owner_name[str(bandID)]["bandName"][0]),str(bands[str(bandID)]["bandName"][0])]
        else:
            owner: str = [str(owner_name[str(bandID)]["bandName"][0]),"其他"]
    else:
        owner: str = str(song_info['author']["username"])
    #---->点赞数
    if offical:
        likes: str = "None"
    else:
        likes: str = str(song_info["likes"])
    #整合数据
    print(f"[I][bangdream-api-chart]: all data collected and start to processing into dict")
    charInfo.update({"name": name})
    charInfo.update({"id": id})
    charInfo.update({"difficult": difficult})
    charInfo.update({"level": level})
    charInfo.update({"bpm": bpm})
    charInfo.update({"count": count})
    charInfo.update({"time": time})
    charInfo.update({"server": server})
    charInfo.update({"owner": owner})
    charInfo.update({"like": likes})
    charInfo.update({"chart": chart})
    #返回数据
    print(f"[I][bangdream-api-chart]: data return")
    return charInfo

#从bestdori请求所有谱面ID
#仅ID列表
def returnAllOfficalSongKey():
    keySet = []#暂存ID信息
    #请求谱面ID记录
    song_url = "https://bestdori.com//api/songs/all.7.json"
    data = requestData(song_url)
    keySet = [key for key in data]
    #返回数据
    return keySet

#从bestdori请求所有谱面名称
#谱面名称→ID字典
def returnAllOfficalSongName():
    nameSet = {}#暂存名称信息
    #请求谱面名称记录
    song_url = "https://bestdori.com//api/songs/all.7.json"
    data = requestData(song_url)
    #取出名称并创建字典
    for key in data:
        id = []
        nameList = data[key]['musicTitle']
        for name in nameList:
            if name == None:
                continue
            #处理同名歌曲
            if name in nameSet:
                id: list = nameSet[name]
                id.append(key)
            else: id = [key]
            nameSet.update({name:id})
    #返回数据
    return nameSet

#从bestdori请求所有乐团名称
#乐团名称→ID字典
def returnAllOfficalBandName():
    nameSet = {}#暂存名称信息
    #请求乐团名称记录
    band_url = "https://bestdori.com/api/bands/all.1.json"
    data = requestData(band_url)
    #取出名称并创建字典
    for key in data:
        for name in data[key]["bandName"]:
            if name in nameSet or name == None:
                continue
            nameSet.update({name:key})
    #返回数据
    return nameSet

#从bestdori请求所有含有该字段的曲目ID
def sreachByName(name: str):
    result = [] #暂存ID列表
    nameList = returnAllOfficalSongName()
    #筛选
    for data in nameList:
        #双方转换至小阶并比对
        #------>允许不完整/模糊搜索
        if name.lower() in data.lower():
            result.extend([id for id in nameList[data] if id not in result])
    return result

#从bestdori请求该乐团所属的所有曲目ID
#支持模糊搜索
def sreachByBand(band: str):
    result = [] #暂存ID列表
    #模糊关键词
    if band.lower() == "ppp":
        band = "Poppin'Party"
    elif band.lower() == "ag":
        band = "Afterglow"
    elif band.lower() == "hhw":
        band = "ハロー、ハッピーワールド！"
    elif band.lower() == "pp" or band.lower() == "p*p":
        band = "Pastel＊Palettes"
    elif band == "萝":
        band = "Roselia"
    elif band == "蝶":
        band = "Morfonica"
    elif band == "母鸡卡":
        band = "Ave Mujica"
    elif band == "梦结":
        band = "夢ノ結唱"
    #请求必须信息
    songList = returnAllOfficalSong()
    nameList = returnAllOfficalBandName()
    #更新乐团名称→小阶: 供模糊搜索
    temp ={} #暂存乐团名称列表
    for n in nameList:
        temp.update({n.lower():nameList[n]})
    nameList = temp
    #模糊匹配乐团信息，返回可能参数 (Band ID)
    bandID = [nameList[name] for name in nameList if band.lower() in name]
    #筛选
    result = [song for song in songList if str(songList[song]["bandId"]) in bandID ]
    return result

#从bestdori请求所有该等级的曲目ID
def sreachByLevel(level: int | str):
    result = [] #暂存ID列表
    level = int(level)
    #请求必须信息
    data = returnAllOfficalSong()
    #筛选
    for key in data:
        song = data[key]
        #比对各种难度
        for difficulty in song['difficulty']:
            levelData = song['difficulty'][difficulty]
            if levelData["playLevel"] == level:
                result.append(key)
                break
    return result

#从bestdori请求所有该曲目种类的曲目ID
def sreachByType(songType: str):
    result = [] #暂存ID列表
    #模糊关键词
    if songType == "原创": songType = "normal"
    elif songType == "动画": songType = "anime"
    elif songType == "翻唱": songType = "tie_up"
    elif songType == "cover": songType = "tie_up"
    elif songType == "covers": songType = "tie_up"
    #请求必须信息
    data = returnAllOfficalSong()
    #筛选
    result = [key for key in data if data[key]["tag"] == songType]
    return result

#从bestdori请求列表内的所有曲目信息
#仅基础信息:
#谱面ID| 谱面名称 | 谱面等级 | 持有者
#谱面ID→信息字典
def requestName(idList: list[str | int]):
    out = {} #暂存输出
    #请求曲目信息
    songList = returnAllOfficalSong()
    #筛选
    for id in idList:
        id = str(id)
        info = {} #暂存曲目信息
        song_info = songList[id]
        #谱面名称
        name: str = getName(song_info['musicTitle'])
        #谱面等级
        level: list = []
        for difficulty in song_info['difficulty']:
            level.append(song_info['difficulty'][difficulty]['playLevel'])
        #持有者
        bandID = str(song_info["bandId"])
        url = "https://bestdori.com//api/bands/main.1.json"
        bands = requestData(url)
        band_url = "https://bestdori.com/api/bands/all.1.json"
        owner = requestData(band_url)
        if bandID in bands:
            owner: list = [owner[str(bandID)]["bandName"][0],str(bands[str(bandID)]["bandName"][0])]
        else:
            owner: list = [owner[str(bandID)]["bandName"][0],"其他"]
        #创建曲目信息
        info.update({"name":name})
        info.update({"level":level})
        info.update({"owner":owner})
        #创建输出字典
        out.update({id: info})
    return out

#查询对应ID是否谱面或存在
def isChart(id: str | int, offical: bool):
    id = str(id)
    if offical:
        return (id in returnAllOfficalSongKey())
    else:
        try:
            requestsChartFromAPI(offical=False, charID=id)
            return True
        except:
            return False
