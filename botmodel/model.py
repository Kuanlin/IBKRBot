import asyncio
from ModelBase import ModelBase
from RESTRequest import RESTRequest
from pprint import pprint as pp

class MyModel(ModelBase):

    async def request(self, messenge_future):
        await self.restRequest.send_message("rest.request", await messenge_future)

    async def requests(self, message_futures:list):
        for messenge_future in message_futures:
            await self.restRequest.send_message("rest.request", await messenge_future)

    async def onSysMessage(self, message:dict):
        pass
    
    async def onRestResponse(self, message:dict):
        print("MyModel: onRestResponse", flush = True)
        pp(message)

    async def modelModifyOrders(self):
        pass

    async def entry(self):
        print("MyModel: Entry", flush = True)
        self.system.on_message = self.onSysMessage
        self.restResponse.on_message = self.onRestResponse
        await self.request(RESTRequest.portfolioLedger())
        

    async def mainloop(self):
        print("MyModel: MainLoop", flush = True)
        #await request([
        #    
        #])
        await asyncio.sleep(0.5)
