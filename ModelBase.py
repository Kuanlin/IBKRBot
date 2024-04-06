import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from MessageBroker import JSONMessenger

class ModelBase():
    
    def __init__(self, name):
        self.name = name
        self.scheduler = AsyncIOScheduler(({'event_loop': asyncio.get_event_loop()}))
        self.scheduler.start()
        self.reqmsgr = JSONMessenger(name = "reqmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.request")
        self.respmsgr = JSONMessenger(name = "respmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.response")
        self.sysmsgr = JSONMessenger(name = "sysmsgr.model", exchange_name = "sys.exchange", routing_key = "sys.message")

    async def request(self, requests:list) -> None:
        assert type(requests) == list
        for r in requests:
            assert type(r) == dict
            reqmsgr.send_message(routing_key="rest.request", r)
            
    async def entry():
        pass

    async def mainloop():
        pass