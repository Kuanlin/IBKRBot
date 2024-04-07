import asyncio, signal, json, importlib
from ModelBase import ModelBase
from ConfigProvider import *
from RESTClient import RESTClient
from MessageBroker import JSONMessenger
use_model = modelconfig["use_model"]
model_name = modelconfig["name"]
Model = vars(importlib.import_module(f"botmodel.{use_model}")).get(model_name)


class BotBase():
    
    def __init__(self, model:ModelBase):
        self.model = model

    async def entry(self):
        await self.model.model_init()
        await self.model.entry()
        await self.mainloop()

    async def mainloop(self):
        while True:
            try:
                while True:
                    await asyncio.sleep(0)
                    try:
                        await asyncio.sleep(0)
                        await self.model.main()
                    except Exception as e:
                        #await self.restReInit()
                        await asyncio.sleep(1)
                        next
            except Exception as e:
                await asyncio.sleep(1)
                next

async def ask_exit(signame):
    system = JSONMessenger(name = "askexit.model", exchange_name = "sys.exchange", routing_key = "sys.message")
    await system.connect()
    await system.send_message( dest_routing_key = "sys.message", message = {"system":"exit"})
    print("got signal %s: exit" % signame)
    print("wait for 3 second")
    await asyncio.sleep(3.0)
    print("loop stopping")
    loop = asyncio.get_event_loop()
    loop.stop()
    print("loop stopped")

async def run():
    while(True):
        #print(".", end="", flush=True)
        await asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
             lambda: asyncio.ensure_future(ask_exit(signame)))
    
    restClient = RESTClient()
    model = Model(name = model_name, default_paused = False)
    bot = BotBase(model)
    await asyncio.gather(run(), bot.entry(), restClient.start())

if __name__=="__main__":
    asyncio.run(main())




