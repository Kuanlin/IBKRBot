import asyncio, aiohttp, json
from MessageBroker import JSONMessenger
from enum import Enum
from RESTRequest import *

MAX_RETRIED = 3

class RESTQueuePriority(Enum):
    DEFAULT = 50
    MIDHIGH = 30 
    HIGH = 20


class RESTSession:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.reqqueue = asyncio.PriorityQueue()
        self.reqmsgr = JSONMessenger(name = "reqmsgr.restclient", exchange_name = "rest.exchange", routing_key = "rest.request")
        self.respmsgr = JSONMessenger(name = "respmsgr.restclient", exchange_name = "rest.exchange", routing_key = "rest.response")
        self.sysmsgr = JSONMessenger(name = "sysmsgr.restclient", exchange_name = "sys.exchange", routing_key = "sys.message")

    async def start(self):
        await self.reqmsgr.connect()
        self.reqmsgr.on_message = self._onRestRequest
        await self.reqmsgr.connect()
        self.respmsgr.on_message = self._onRestResonse
        await self.respmsgr.connect()
        self.sysmsgr.on_message = self._onSysMessage
        await self.sysmsgr.connect()
        await self._restClientSession()


    async def _onRestRequest(self, message_body):
        await self.reqqueue.put( (RESTQueuePriority, message_body) )


    async def _onRestResponse(self):
        #if yes no to push
        pass


    async def _onSysMessage(self):
        pass

    async def onResponse(self):
        pass
    

    async def _restClientSession(self) -> None:
        headers = {"User-Agent":"JAGMAGMAG/0.0.1 GGCG"}
        while(True):
            try:
                await self.onClientInit()
                while(True):
                    await asyncio.sleep(0)
                    async with aiohttp.ClientSession(
                        IBKRClientPortalURI,
                        connector=aiohttp.TCPConnector(verify_ssl=False)
                    ) as session:
                        
                        priority, request = await self.reqqueue.get()

                        try:
                            async with session.request(
                                method = request["method"],
                                url = request["url"],
                                headers = headers | {} if not request.get("headers") else request.get("headers"),
                                params = request["params"],
                                data = request.get("data") if request.get("data") != None else "{}",
                                allow_redirects = False,
                                timeout = request["timeout"]
                            ) as response:
                                _status = response.status
                                _content = (await resp.content.read()).decode('utf8')

                                _chain = vars(RESTRequest).get(request.get("chain"))
                                if _chain:
                                    _chain_param = request.get("respchain_kwarg")
                                    _chain_request = await _chain(_content, **_chain_param)
                                    if _chain_request:
                                        self.reqqueue.put((RESTQueuePriority.HIGH,chain_request))
                                else:
                                    _jcontent = json.loads(_content)
                                    self.respmsgr.send_message("rest.response", _jcontent)

                        except (
                            aiohttp.ServerTimeoutError,
                            aiohttp.client_exceptions.ClientConnectorError
                        ) as e:
                            retried = request.get("retried")
                            if not retried:
                                request["retried"] = 1
                                self.requeue.put((RESTQueuePriority.MIDHIGH, request))
                            elif retried < MAX_RETRIED:
                                request["retried"] = retried + 1
                                self.requeue.put((RESTQueuePriority.MIDHIGH, request))
                            else:
                                _msg = { "status":"failed", "request":request, "retried":retried }
                                self.respmsgr.send_message("rest.response", _msg )

                        await asyncio.sleep(0)

            except Exception as e:
                await asyncio.sleep(0)





