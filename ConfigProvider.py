import json

_f = open("./config/dockconf.json", "r")
_j = json.load(_f)
_f2 = open("./config/ibkr.json", "r")
_j2 = json.load(_f2)
_f3 = open("./config/model.json", "r")
_j3 = json.load(_f3)
auths = _j
ibkr = _j2
modelconfig = _j3
