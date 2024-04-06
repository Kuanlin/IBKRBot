import asyncio
from ModelBase import ModelBase
from restRequest import *

class MyModel(ModelBase):

    async def onSysMessage(self, message:dict):
        pass
    
    async def onRestResponse(self, message:dict):
        pass

    async def entry(self):
        print("MyModel Entry")
        self.system.on_message = onSysMessage
        self.restResponse.on_message = onRestResponse

    async def mainloop(self):
        print("MyModel MainLoop")
        #await request([
        #    
        #])
        await asyncio.sleep(0.5)