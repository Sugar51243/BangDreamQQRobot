from request_from_api.request_from_api import requestData

allowedServers = ["jp", "cn", "tw", "en", "kr"]

def checkServerAble(server):
    for allowedServer in allowedServers:
        if server == allowedServer:
            return True
    return False

def testgetUser(playerID, server):
    
    if checkServerAble(server) == False:
        message = "服务器参数错误"
    
    try:
        url = f"https://bestdori.com/api/player/{server}/{playerID}"
        message = requestData(url)
    except:
        message = "服务器网络连接出错"
    
    if message['data']['profile'] == None:
        message = "玩家不存在"
    
    return message

user = testgetUser("1009206924","cn")
print(user)