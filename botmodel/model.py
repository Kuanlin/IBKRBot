import asyncio
from ModelBase import ModelBase
from RESTRequest import RESTRequest
from pprint import pprint as pp

class MyModel(ModelBase):

    async def onSysMessage(self, message:dict):
        pass
    
    async def onRestResponse(self, message:dict):
        print("MyModel: onRestResponse", flush = True)
        pp(message)

    async def portfolioLedger(self):
        print("MyModel: portfolioLedger", flush = True)
        await self.restRequest.send_message("rest.request", await RESTRequest.portfolioLedger())

    async def modelModifyOrders(self):
        pass

    async def modelDeleteOrders(self):
        #insert model order decision to database
        #dbmsgr.send_messages(..//)
        #restRequest.send_message([ DeleteOrders ...])
        #restRequest.send_message([ check live Orders ])
        pass

    async def modelPlaceOrders(self):
        #insert model order decision to database
        #dbmsgr.send_messages(..//)
        #restRequest.send_message([ PlaceOrders ...])
        #restRequest.send_message([ check live Orders ])
        pass

    async def onRestRequest(self, message):
        print("MyModel: onRestRequest")
        pp(message)

    async def entry(self):
        print("MyModel: Entry", flush = True)
        #self.system.on_message = self.onSysMessage
        self.restRequest.on_message = self.onRestRequest
        self.restResponse.on_message = self.onRestResponse
        await self.portfolioLedger()

    async def mainloop(self):
        print("MyModel: MainLoop", flush = True)
        #await request([
        #    
        #])
        await asyncio.sleep(0.5)
