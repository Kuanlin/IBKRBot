import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from MessageBroker import JSONMessenger

class ModelBase():
    

    def __init__(self, name, default_paused = True):
        self.name = name
        self.scheduler = AsyncIOScheduler(({'event_loop': asyncio.get_event_loop()}))
        self.scheduler.start()
        self.restRequest = JSONMessenger(name = "reqmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.request")
        self.restResponse = JSONMessenger(name = "respmsgr.model", exchange_name = "rest.exchange", routing_key = "rest.response")
        self.system = JSONMessenger(name = "sysmsgr.model", exchange_name = "sys.exchange", routing_key = "sys.message")
        #self.fromUser = JSONMessenger(name = "userreqmsgr.model", exchange_name = "user.exchange", routing_key = "usr.request")
        #self.toUser = JSONMessenger(name = "userrespmsgr.model", exchange_name = "user.exchange", routing_key = "usr.response")
        self.isPaused = default_paused
        self.exit = False
    

    async def model_init(self):
        print("Model model_init", flush = True)
        await self.restRequest.connect()
        await self.restResponse.connect()
        await self.system.connect()
        self.system.on_message = self.onSysMessage
        #await self.fromUser.connect()
        #await self.toUser.connect()
        print("Model model_init end", flush = True)


    async def request(self, requests:list) -> None:
        print("Model request", flush = True)
        assert type(requests) == list
        for r in requests:
            assert type(r) == dict
            await self.restRequest.send_message(routing_key="rest.request", message = r)


    async def onSysMessage(self, message):
        if message.get("system") == "exit":
            print("Model receive Exit Message")
            self.exit = True            


    async def pasued(self):
        self.isPaused = True


    async def play(self):
        self.isPaused = False

            
    async def entry(self):
        pass


    async def main(self):
        await asyncio.sleep(0)
        print(f"In Model Main {self.isPaused} {self.exit}", flush = True)
        try:
            while(not self.exit):
                print(f"xx: {self.isPaused} {self.exit}", flush = True)
                await asyncio.sleep(0)
                while(self.isPaused and not self.exit):
                    await asyncio.sleep(0.5)
                print("In Model Main While", flush = True)
                await self.mainloop()
        except Exception as e:
            print("in model main exception:")
            print(e)
        
        await asyncio.sleep(2)
        await self.restRequest.close()
        await self.restResponse.close()
        await self.system.close()

            
    async def mainloop(self):
        await asyncio.sleep(0.5)
