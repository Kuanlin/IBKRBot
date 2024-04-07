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
        self.exit = False
        self.system = JSONMessenger(name = "botbase.sys", exchange_name = "sys.exchange", routing_key = "sys.message")

    async def entry(self):
        await self.model.model_init()
        await self.model.entry()
        await self.mainloop()
        await self.system.connect()
        systme.on_message = self.onSysMessage

    async def onSysMessage(self, message):
        if message.get("system") == "exit":
            print("Bot receive Exit Message")
            self.exit = True

    async def mainloop(self):
        while not self.exit:
            try:
                while not self.exit:
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
    print("got signal %s: exit" % signame)
    await system.send_message( dest_routing_key = "sys.message", message = {"system":"exit"})
    print("3 seconds before loop stops.")
    await asyncio.sleep(3.0)
    loop = asyncio.get_event_loop()
    loop.stop()
    print("loop stopped")


async def main():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
             lambda: asyncio.ensure_future(ask_exit(signame)))

    restClient = RESTClient()
    model = Model(name = model_name, default_paused = False)
    bot = BotBase(model)
    await asyncio.gather(bot.entry(), restClient.start())

if __name__=="__main__":
    asyncio.run(main())




