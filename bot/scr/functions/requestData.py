import requests
import json


#File to request data from network api
#Handling empty data return and network error

def requestData(url: str):
    #try catch expeted: ( Network Exception(s) |  JSONDecode Exception(s) )
    try:
        #Get response(s) from url
        response = requests.get(url)
        #Json the data
        data:dict = response.json()
    except Exception as e:
        #Error message
        print("[request-from-api: Error]: Data request error from: " + url)
        print("[request-from-api: Error]: Error details belowe:")
        print("[request-from-api: Error]: " + str(e))
        #return the error
        raise e
    #return
    return data