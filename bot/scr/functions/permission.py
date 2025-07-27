from ncatbot.core import MessageChain
# ========= 导入自定义模块 ==========
from functions.fileHandler import readJson, writeJson

#registrate owner permission
def registration(newOwners = []):
    path = "data/owner.json"
    try:
        owners = readJson(path)["owner"]
    except:
        writeJson(path=path, data={"owner":newOwners})
        return newOwners
    if len(newOwners) > 0:
        owners.extend(newOwners)
        owners=list(set(owners))
        writeJson(path=path, data={"owner":owners})
    return owners

def registrationUpdate(group_id: int | str ,functionType: str):
    group_id = str(group_id)
    data = readJson("command/data/registration.json")
    functions = data[group_id]
    if functionType not in functions:
        functions.append(functionType)
        data.update({group_id:functions})
        writeJson(path="command/data/registration.json", data=data)
        print(f"[I][Function Registration]: Group [{group_id}] Registration For Function [bangdream] success")
        message = MessageChain([f"注册成功"])
    else:
        print(f"[I][Function Registration]:  Function [bangdream] already Registrationed for group [{group_id}]")
        message = MessageChain([f"功能已注册, 请勿重复注册"])
    return message