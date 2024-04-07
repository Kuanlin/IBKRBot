import aiohttp
import asyncio, json
from typing import Union
from ConfigProvider import ibkr

DEFAULT_ACCOUNTID = ibkr.get("DEFAULT_ACCOUNTID")
DEFAULT_ORDER_CONFIRM = ibkr.get("DEFAULT_ORDER_CONFIRM")
DEFAULT_TIMEOUT = 3

class OrderSide:
    BUY = "buy"
    SELL = "sell"
_OrderSide = [ OrderSide.__getattribute__(OrderSide, x) for x in OrderSide.__dict__ if not x.startswith("__") and not x.endswith("__") ]

class OrderType:
    MARKET = "MKT"
    LIMIT = "LMT"
_OrderType = [ OrderType.__getattribute__(OrderType, x) for x in OrderType.__dict__ if not x.startswith("__") and not x.endswith("__") ]

class OrderTIF:
    DAY = "DAY"
_OrderTIF = [ OrderTIF.__getattribute__(OrderTIF, x) for x in OrderTIF.__dict__ if not x.startswith("__") and not x.endswith("__") ]


class RESTRequest:
    
    async def liveOrders(
        filters:list = [],
        force: bool = False, 
        accountId: str = DEFAULT_ACCOUNTID, 
        timeout: int = DEFAULT_TIMEOUT) -> dict:

        assert type(accountId) == str
        assert len(accountId) > 0
        assert type(force) == bool
        fil = ",".join(filters)
        fil = "filters="+fil+"&"
        fc = "force=true&" if force else "force=false&"
        return {
            "method": r"GET",
            "url": f"/v1/api/iserver/account/orders?{fil}{fc}accountId={accountId}",
            "params": "",
            "timeout": timeout }


    async def orderStatus(
        orderId: Union[int, str], timeout: int = DEFAULT_TIMEOUT) -> dict:

        assert type(orderId) != int and type(orderId) != str
        assert type(orderId) == int or type(orderId) == str
        oid = str( orderId if type(orderId)==int else int(orderId) )
        return {
            "method": r"GET",
            "url": f"/v1/api/iserver/account/order/status/{oid}",
            "params": "",
            "timeout": timeout }


    async def placeOrders(
        orders: list,
        accountId: str = DEFAULT_ACCOUNTID,
        timeout: int = DEFAULT_TIMEOUT) -> dict:

        assert restOrderConfirmed == True
        assert type(orders) == list
        assert len(orders) > 0
        assert all( [ type(od) == Order for od in orders ] )
        assert type(accountId) == str
        assert len(accountId) > 0

        acctId = accountId
        orderList = {"orders": [ od.toDict() for od in orders ]}
        orderListStr = json.dumps(orderList)
        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/account/{accountId}/orders",
            "params": "",
            "data": orderListStr,
            "respchain": "respondChain_OrdersApprov" if DEFAULT_ORDER_CONFIRM else None,
            "respchain_kwarg": { "accountId": accountId },
            "timeout": timeout }


    async def respondChain_OrdersApprov(content, **kwargs) -> dict:
        jcontent = json.loads(content)
        replyId = jcontent[0].get("id")
        #print(f"chain:::/v1/api/iserver/reply/{ replyId }")
        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/reply/{ replyId }",
            "params": "",
            "data": r'{"confirmed":true}',
            "timeout": kwargs.get("timeout") if kwargs.get("timeout") else DEFAULT_TIMEOUT }


    async def modifyOrder(
        orderId: str,
        conid: int = None,
        price: float = None,
        quantity: float = None,
        orderType: str = None,
        side: str = None,
        tif: str = None,
        accountId: str = DEFAULT_ACCOUNTID, 
        timeout: int = DEFAULT_TIMEOUT) -> dict:
        
        dataDict = {
            "price": price,
            "quantity": quantity, }
        if price:
            dataDict["price"] = price
        if quantity:
            dataDict["quantity"] = quantity
        if conid:
            dataDict["conid"] = conid
        if orderType:
            dataDict["orderType"] = orderType
        if side:
            dataDict["side"] = side
        if tif:
            dataDict["tif"] = tif

        dataStr = json.dumps(dataDict)

        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/account/{accountId}/order/{orderId}",
            "params": "",
            "data": dataStr,
            "respchain": "respondChain_ModifyOrdersApprov" if DEFAULT_ORDER_CONFIRM else None,
            "respchain_kwarg": { "accountId": accountId },
            "timeout": timeout }


    async def respondChain_ModifyOrdersApprov(content, **kwargs) -> dict:
        jcontent = json.loads(content)
        replyId = jcontent[0].get("id")
        print(f"chain:::/v1/api/iserver/reply/{ replyId }")
        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/reply/{ replyId }",
            "params": "",
            "data": r'{"confirmed":true}',
            "timeout": kwargs.get("timeout") if kwargs.get("timeout") else DEFAULT_TIMEOUT }


    async def cancelOrder(
        orderId: Union[int, str],
        accountId: str = DEFAULT_ACCOUNTID,
        timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        assert type(orderId) == int or type(orderId) == str
        oid = str( orderId if type(orderId)==int else int(orderId) )
        return {
            "method": r"DELETE",
            "url": f"/v1/api/iserver/account/{accountId}/order/{oid}" }


    #how we get future's conid
    async def securityFuturesBySymbols(symbols:list = [], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(symbols) == list
        assert len(symbols) > 0
        assert all( [ type(s) == str and len(s) > 0 for s in symbols ] )
        sbs = ",".join(symbols)
        return {
            "method": r"GET",
            "url": f"/v1/api/trsrv/futures?symbols={sbs}",
            "params": "",
            "timeout": timeout }


    #how we get stock's conid
    async def securityStocksBySymbols(symbols:list = [], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(symbols) == list
        assert len(symbols) > 0
        assert all( [ type(s) == str and len(s) > 0 for s in symbols ] )
        sbs = ",".join(symbols)
        return {
            "method": r"GET",
            "url": f"/v1/api/trsrv/stocks?symbols={sbs}",
            "params": "",
            "timeout": timeout }

    async def profitAndLoss(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/iserver/account/pnl/partitioned",
            "params": "",
            "timeout": timeout }


    async def portfolioAccounts(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/portfolio/accounts",
            "params": "",
            "timeout": timeout }


    async def portfolioSubaccounts(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/portfolio/subaccounts",
            "params": "",
            "timeout": timeout }


    async def positions(pageId: int = 0, accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and pageId >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout }
    

    async def positionsAll(pageId: int = 0, accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and pageId >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout,
            "respchain": RESTRequests.respondChain_PositionNextPage,
            "respchain_kwarg": { "accountId": accountId, "pageId" : pageId+1, "timeout": timeout }, }


    async def respondChain_PositionNextPage(content, **kwargs):
        if content == "" or content=="[]":
            return None
        accountId = kwargs["accountId"]
        pageId = kwargs["pageId"]
        timeout = kwargs["timeout"]
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and pageId >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout,
            "respchain": RESTRequests.respondChain_PositionNextPage,
            "respchain_kwarg": { "accountId": accountId, "pageId" : pageId+1 }, }


    async def positionsbyConid(conid: str = None, acctId: str = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(acctId) == str and len(acctId) > 0
        assert type(conid) == str and len(conid) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{acctId}/position/{conid}",
            "params": "",
            "timeout": timeout }

    
    #Invalidate Backend Portfolio Cache not impl.
    async def invalidateBackendPortfolio():
        raise NotImplementedError


    async def portfolioSummary(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/summary",
            "params": "",
            "timeout": timeout }

    async def portfolioLedger(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/ledger",
            "params": "",
            "timeout": timeout }
    
    async def PositionNContractInfo(conid: str = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(conid) == str and len(conid) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/positions/{conid}",
            "params": "",
            "timeout": timeout }