import json

_f = open("./scripts/dockconf.json", "r")
_j = json.load(_f)
_f2 = open("./scripts/ibkr.json", "r")
_j2 = json.load(_f2)
auths = _j
ibkr = _j2
