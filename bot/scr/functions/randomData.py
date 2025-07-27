import random

#Random number
def randomDetermination(target: int):
    num = random.randint(0, 99)
    if num <= target:
        return True
    return False

def randomIndex(inList: list | dict):
    keySet = []
    for key in inList:
        keySet.append(key)
    idx = random.randint(0, len(inList)-1)
    return keySet[idx]
