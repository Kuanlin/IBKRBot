import asyncio, signal
from ModelBase import ModelBase

class BotBase():
    
    def __init__(self, model:ModelBase):
        pass

    async def run(self):
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




class IBKRBot():

    def __init__(bot:BotBase, restv
import asyncio, signal
from ModelBase import ModelBase

class BotBase():
import asyncio

import aiohttp


class RESTSession:


    def __init__(self):
        pass

    
    def onResponse(self):
        pass
    

    def restClientSession(self) -> None:
        pass
    
    def __init__(self, model:ModelBase):
        pass

import asyncio, signal
from ModelBase import ModelBase

class BotBase():
    
    def __init__(self, model:ModelBase):
        pass

    async def run(self):
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




class IBKRBot():

    def __init__(bot:BotBase, restv
import asyncio, signal
from ModelBase import ModelBase

class BotBase():
    
    def __init__(self, model:ModelBase):
        pass

    async def run(self):
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




class 





async def ask_exit(signame):

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






async def ask_exit(signame):

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

    async def run(self):
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




class 





async def ask_exit(signame):

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






async def ask_exit(signame):

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

