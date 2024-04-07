import asyncio, aiohttp, json
from MessageBroker import JSONMessenger
from enum import Enum
from RESTRequest import *
from pprint import pprint as pp

MAX_RETRIED = 3

IBKRClientPortalURI = "https://localhost:5000"

class RESTQueuePriority(Enum):
    DEFAULT = 50
    MIDHIGH = 30 
    HIGH = 20


class RESTClient:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.reqqueue = asyncio.PriorityQueue()
        self.reqmsgr = JSONMessenger(name = "reqmsgr.restclient", exchange_name = "rest.exchange", routing_key = "rest.request")
        self.respmsgr = JSONMessenger(name = "respmsgr.restclient", exchange_name = "rest.exchange", routing_key = "rest.response")
        self.sysmsgr = JSONMessenger(name = "sysmsgr.restclient", exchange_name = "sys.exchange", routing_key = "sys.message")
        self.exit = False

    async def start(self):
        self.reqmsgr.on_message = self._onRestRequest
        await self.reqmsgr.connect()
        self.respmsgr.on_message = self._onRestResponse
        await self.respmsgr.connect()
        self.sysmsgr.on_message = self._onSysMessage
        await self.sysmsgr.connect()
        await self._restClientSession()


    async def _onRestRequest(self, message_body):
        print("RESTClient onRestRequest", flush=True)
        pp(message_body)
        await self.reqqueue.put( (RESTQueuePriority, message_body) )


    async def _onRestResponse(self, message_body):
        #if yes no to push
        pass

    async def _onSysMessage(self, message_body):
        print("_onSysMessage")
        pp(message_body)
        if message_body.get("system") == "exit":
            print("RESTClient receive Exit Message")
            self.exit = True

    async def onResponse(self):
        pass
    
    async def onClientInit(self):
        print("RESTClient onClientInit")

    async def _restClientSession(self) -> None:
        headers = {"User-Agent":"JAGMAGMAG/0.0.1 GGCG"}
        while(self.exit == False):
            try:
                await self.onClientInit()
                while(self.exit == False):
                    await asyncio.sleep(0)
                    async with aiohttp.ClientSession(
                        IBKRClientPortalURI,
                        connector=aiohttp.TCPConnector(verify_ssl=False)
                    ) as session:
                        while(self.reqqueue.empty() or self.exit == False):
                            await ayncio.sleep(0.1)
                        if self.exit:
                            break
                        priority, request = await self.reqqueue.get()
                        #print("RESTCleintSession")
                        #pp(request)
                        #print("url:", IBKRClientPortalURI+request["url"])
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
                                _content = (await response.content.read()).decode('utf8')
                                #print("response", flush = True)
                                #print("response_status:", _status, flush = True)
                                #print("content:", _content, flush = True)

                                _chain = request.get("chain")
                                if _chain:
                                    _chain_request = vars(RESTRequest).get(_chain)
                                    _chain_param = request.get("respchain_kwarg")
                                    _request = await _chain_request(_content, **_chain_param)
                                    if _request:
                                        self.reqqueue.put((RESTQueuePriority.HIGH, _request))
                                    else:
                                        raise Exception("Unexpect Chain Error")
                                else:
                                    _jcontent = json.loads(_content)
                                    await self.respmsgr.send_message("rest.response", _jcontent)

                        except (
                            aiohttp.ServerTimeoutError,
                            aiohttp.client_exceptions.ClientConnectorError
                        ) as e:
                            print("CLIENT EXCEPTION")
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
                print(e)
                await asyncio.sleep(0)

        await asyncio.sleep(2)
        print("REST MSGR CLOSE")
        await self.reqmsgr.close()
        await self.respmsgr.close()
        await self.sysmsgr.close()





