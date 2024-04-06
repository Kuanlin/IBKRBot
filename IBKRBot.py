import asyncio, signal, json, importlib
from ModelBase import ModelBase
from ConfigProvider import *

use_model = modelconfig["use_model"]
model_name = modelconfig["name"]
model = var(importlib.import_module(f"botmodel.{use_model}")).get(model_name)

class BotBase():
    
    def __init__(self, model:ModelBase):
        self.model = model

    async def entry(self):
        await self.model.entry()

    async def mainloop(self):
        while True:
            try:
                while True:
                    await asyncio.sleep(0)
                    try:
                        await asyncio.sleep(0)
                        await self.mainloop()
                    except Exception as e:
                        await self.restReInit()
                        await asyncio.sleep(1)
                        next
            except Exception as e:
                await asyncio.sleep(1)
                next
        
    async def mainloop():
        await asyncio.sleep(0)

async def ask_exit()
    print("got signal %s: exit" % signame)
    await asyncio.sleep(10.0)
    loop = asyncio.get_event_loop()
    loop.stop()

async def run():
    while(True):
        print(".", end="", flush=True)
        await asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
             lambda: asyncio.ensure_future(ask_exit(signame)))
    await asyncio.gather(run())

if __name__=="__main__":
    asyncio.run(main())




