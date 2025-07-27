# ========= 导入必要Python内置模块 ==========
import io, json, os


#list file
def listFile(path: str):
    #IO Error excepted -> dir not found
    try:
        fileList = os.listdir(path)
        output = []
        for p in fileList:
            output.append(f"{path}/{p}")
        return output
    except FileNotFoundError as ioE:
        print(f"[Folder Reader]: No folder call {path}")
        print(f"[Folder Reader]: New dir will be newed")
        os.makedirs(path)
        return []

#read data in normal format
def readFile(path: str):
    #IO Error excepted -> file not found
    try:
        #Open file in read mode
        with open(path, "r", encoding="utf-8") as file:
            data = file.read()
        #logging result in backend
        #return
        return data
    #Exception Handle
    except FileNotFoundError as ioE:
        #logging result in backend
        print(f"[W][File reader]: File in path [{path}] open failed")
        print(f"[W][File reader]: A file will be newed")
        #create a new file in dir
        with open(path, "w", encoding="utf-8") as file:
            file.write()
        #return
        return

#read data from file in json format
def readJson(path: str):
    #JSONDecodeError excepted -> input not in json format
    try:
        #read data from file
        data = readFile(path)
        #conversion as a json object
        output = json.loads(data)
        #return
        return output
    #Exception Handle
    except json.JSONDecodeError as jsonE:
        #logging result in backend
        print(f"[W][Json reader]: File not in json format")
        print(f"[W][Json reader]: File will be renewed")
        #renew the file as json format
        writeJson(path=path)
        #return
        return {}

#write json data into file
def writeJson(path: str, data = {}):
    #JSONDecodeError excepted -> input not in json format
    with open(path, "w") as file:
        json.dump(data,file)

#write json data into file
def writeFile(path: str, data):
    #JSONDecodeError excepted -> input not in json format
    with open(path, "wb") as file:
        file.write(data)