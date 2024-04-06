import aiohttp
import asyncio, json
from typing import Union



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



class RestRequest:
    
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


    async def respondChain_OrdersApprov(content, **kwargs):
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


    async def respondChain_ModifyOrdersApprov(content, **kwargs):
        jcontent = json.loads(content)
        replyId = jcontent[0].get("id")
        print(f"chain:::/v1/api/iserver/reply/{ replyId }")
        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/reply/{ replyId }",
            "params": "",
            "data": r'{"confirmed":true}',
            "timeout": kwargs.get("timeout") if kwargs.get("timeout") else DEFAULT_TIMEOUT }

