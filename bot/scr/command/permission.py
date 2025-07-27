# ========= 导入自定义模块 ==========
from functions.fileHandler import readJson, writeJson

#function registration for group
def returnRegistration(groupID = int):
    path = "command/data/registration.json"
    data = readJson(path=path)
    try:
        return data[str(groupID)]
    except:
        data.update({str(groupID):["general"]})
        writeJson(path=path, data=data)
        return data[str(groupID)]
