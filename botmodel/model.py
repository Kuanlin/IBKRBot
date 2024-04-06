import asyncio
from ModelBase import ModelBase

class MyModel(ModelBase):

    async def entry():
        print("MyModel Entry")

    async def mainloop():
        print("MyModel MainLoop")
        await asyncio.sleep(0.5)