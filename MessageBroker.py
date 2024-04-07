import asyncio
import aio_pika
import json
from ConfigProvider import auths
from pprint import pprint as pp

class Messenger:
    
    def __init__(self, name, exchange_name, routing_key):
        self.queue_name = name
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        
    async def connect(self):
        _id, _pwd = auths.get("rmq").get("account"), auths.get("rmq").get("password")
        _uri = f"amqp://{_id}:{_pwd}@localhost/"
        self.connection = await aio_pika.connect_robust(_uri)
        self.channel = await self.connection.channel()        
        self.exchange = await self.channel.declare_exchange(self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        await self.queue.consume(self.handle_message, no_ack=False)
        await self.queue.bind(self.exchange_name, routing_key=self.routing_key)
        #await asyncio.Future()

    async def handle_message(self, message):
        async with message.process():
            await self.on_message(message.body.decode())

    async def on_message(self, message_body):
        raise NotImplementedError            

    async def send_message(self, dest_routing_key, message):
        await self.exchange.publish(
            aio_pika.Message( body = message.encode() ),
            routing_key = dest_routing_key )


class JSONMessenger(Messenger):
    
    async def handle_message(self, message):
        async with message.process():
            await self.on_message(json.loads(message.body.decode()))

    async def on_message(self, message):
        raise NotImplementedError

    async def send_message(self, dest_routing_key, message):
        assert type(message) == str or type(message) == dict
        print("JSONMessenger.send_message")
        pp(message)
        if type(message) == dict:
            message = json.dumps(message)
        await self.exchange.publish(
            aio_pika.Message( body = message.encode() ),
            routing_key = dest_routing_key )

