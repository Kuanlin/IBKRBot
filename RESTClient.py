import asyncio, aiohttp, json
from Messenger import Messenger

class RESTSession:


    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.reqmsg = Messenger("rest.request")
        self.respmsg = Messenger("rest.response")
        self.sysmsg = Messenger("sys.messenge")


    
    def onResponse(self):
        pass
    

    def restClientSession(self) -> None:
        pass
