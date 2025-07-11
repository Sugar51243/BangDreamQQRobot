import json



#File to handling loacl file IO
#Handling empty data return and file error

#Path Handling
#Please handling all your file io path over here
# User Binding Data -> command: "绑定玩家"
global userBindingPath
userBindingPath = "data/Save/data.txt" #change the value here

# Song Name Sreaching Key Set -> command: "官谱"
global sreachingKeyPath
sreachingKeyPath = "data/sreachingKey/keyset.txt" #change the value here

# Chart Image saving Path: For Saving the chart Image -> command: "官谱" | "查谱"
global ChartImageSavingPath
ChartImageSavingPath = "data/Image/" #change the value here


#Function
# Read Data From File -> Change It As Json
def readDataFrom(path):
    #try catch expeted: ( FileIO Exception(s) |  JSONDecode Exception(s) )
    try:
        #Open file with encoder utf-8 in read only mode
        with open(path, 'r', encoding="utf-8") as f:
            #Json the data
            data = json.load(f)
    except Exception as e:
        #Error message
        print("[fileIO-handler: Error]: File reading error from: " + path)
        print("[fileIO-handler: Error]: Empty data body will be returned")
        print("[fileIO-handler: Error]: Error details belowe:")
        print("[fileIO-handler: Error]: " + str(e))
        #init empty data body
        data = {}
    #return
    return data

# Read Data Into File: In Json
def writeDatainFile(path, data):
    #try catch expeted: ( FileIO Exception(s) |  JSONDecode Exception(s) )
    try:
        #Open file with encoder utf-8 in write only mode
        #It will clear all the data inside file, please read whole file before using
        with open(path, 'w', encoding="utf-8") as f:
            #Json the data and write it into file
            json.dump(data, f)
    except Exception as e:
        #Error message
        print("[fileIO-handler: Error]: File writing error to: " + path)
        print("[fileIO-handler: Error]: No action will be implement in this action")
        print("[fileIO-handler: Error]: Error details belowe:")
        print("[fileIO-handler: Error]: " + str(e))
