import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from MessageBroker import JSONMessenger

class ModelBase():
    
    def __init__(self, name):
        self.name = name
        self.scheduler = AsyncIOScheduler(({'event_loop': asyncio.get_event_loop()}))
        self.scheduler.start()
        self.restRequest = JSONMessenger(name = "reqmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.request")
        self.restResponse = JSONMessenger(name = "respmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.response")
        self.system = JSONMessenger(name = "sysmsgr.model", exchange_name = "sys.exchange", routing_key = "sys.message")
        self.fromUser = JSONMessenger(Name = "userreqmsgr.model", exchange_name = "user.exchange", routing_key = "usr.request")
        self.toUser = JSONMessenger(Name = "userrespmsgr.model", exchange_name = "user.exchange", routing_key = "usr.response")
        self.isPaused = True

    async def request(self, requests:list) -> None:
        assert type(requests) == list
        for r in requests:
            assert type(r) == dict
            reqmsgr.send_message(routing_key="rest.request", message = r)


    async def pasued(self):
        self.isPaused = True


    async def play(self):
        self.isPaused = False

            
    async def entry(self):
        pass


    async def main(self):
        while(True):
            while(isPaused):
                asyncio.sleep(0.5)
            await asyncio.sleep(0) 
            await mainloop()
            


    async def mainloop(self):
        pass