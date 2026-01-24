from .ListStore import ListStore
from .SetStore import SetStore


storeSet = SetStore()
storeSet.push(5)
storeSet.push(3)
storeSet.push(12)
storeSet.push(4)
# print(storeSet)

storeList = ListStore()
storeList.push(14)
storeList.push(7)
storeList.push(23)
storeList.push(2)
# print(storeList)
storeList.pop()

print(storeSet)
for e in storeList:
    print(e)