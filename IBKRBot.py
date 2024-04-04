import asyncio
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
        await asyncio.sleep(0.5)