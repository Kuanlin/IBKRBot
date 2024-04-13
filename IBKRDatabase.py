import asyncio, asyncpg
from ConfigProvider import auths
from MessageBroker import JSONMessenger

ACCOUNT = auths.get("pdb").get("account")
PASSWORD = auths.get("pdb").get("password")
DATABASE = auths.get("pdb").get("database")

class Database:
    def __init__(self):
        self.conn = None

    async def async_init(self):
        self.conn = await asyncpg.connect(
            user=ACCOUNT, password=PASSWORD,
            database='', host='127.0.0.1')

        #create database
        stmt = (
            r"SELECT datname FROM pg_catalog.pg_database WHERE datname = $1;"
        )
        result = await self.conn.fetch(stmt, DATABASE)
        if (len(result)==0):
            await self.conn.execute(f"CREATE DATABASE {DATABASE}")
        self.conn = await asyncpg.connect(
            user=ACCOUNT, password=PASSWORD,
            database=DATABASE, host='127.0.0.1')

        #create enum
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status') THEN "
                    r"CREATE TYPE status AS ENUM ('stop', 'active', 'liquidating', 'obsolete');"
                r"END IF;"
            r"END $$;" )
        #print(stmt)
        await self.conn.execute(stmt)

        #create table stocks
        stmt = (
            r"CREATE TABLE IF NOT EXISTS stocks ("
                r"id SERIAL, conid INT, "
                r"name Varchar(255),"
                r"exchange Varchar(255), timestamps timestamp,"
                r"PRIMARY KEY(id)"
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)
        
        #create table modelconfigs
        stmt = (
            r"CREATE TABLE IF NOT EXISTS modelconfigs ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"initvalue numeric(20,5) NOT NULL, "
                r"leverage numeric(10, 5) NOT NULL, "
                r"numofsinglespread INT NOT NULL, "
                r"spreadsteppriceratio numeric(12, 5) NOT NULL, "
                r"spreadsteppriceminimal numeric(12, 5) NOT NULL, "
                r"statuscode status, timestamps timestamp, "
                r"finalpnl numeric(20, 5), "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ) "
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)

        #create table modelpnls
        stmt = (
            r"CREATE TABLE IF NOT EXISTS modelpnls ( "
                r"id SERIAL, stkid INT NOT NULL, cfgid INT NOT NULL, "
                r"realizedpnl numeric(20,5), timestamps timestamp, "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ), "
                r"FOREIGN KEY(cfgid) REFERENCES configs(id), "
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)


        #create enum sidetype: buy/sell
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sidetype') THEN "
                    r"CREATE TYPE sidetype AS ENUM ('BUY', 'SELL');"
                r"END IF;"
            r"END $$;" )
        await self.conn.execute(stmt)

        #create enum ordertype: LMT, MKT, IOC
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ordertype') THEN "
                    r"CREATE TYPE ordertype AS ENUM ('LMT', 'MKT');"
                r"END IF;"
            r"END $$;" ) 
        await self.conn.execute(stmt)


        #for bot actions
        stmt = (
            r"CREATE TABLE IF NOT EXISTS modelactions ( "
                r"id SERIAL, "
                r"cfgid INT NOT NULL, "
                r"cash, marketprice, quantity, "
            r");"
        )

        #create table model orders
        stmt = (
            r"CREATE TABLE IF NOT EXISTS modelorders ( "
                r"id SERIAL, actionid INT NOT NULL, " 
                r"stkid INT NOT NULL, "
                r"cfgid INT NOT NULL, "
                r"side sidetype, "
                r"price numeric(20,5), "
                r"quantity numeric(20,5), "
                r"type ordertype, "
                r"placed BOOLEAN, "
                r"timestamps timestamp, "
                r"PRIMARY KEY(id), "
                r"FOREIGN KEY(actionid) REFERENCES modelactions(id), "
                r"FOREIGN KEY(stkid) REFERENCES stocks(id), "
                r"FOREIGN KEY(cfgid) REFERENCES modelconfigs(id) "
            r");" )
        await self.conn.execute(stmt)

        #create table order history
        stmt = (
            r"CREATE TABLE IF NOT EXISTS orderhistory ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"orderid INT NOT NULL, "
                #r"cfgid INT NOT NULL, " #if we check from orders, there's no cfgid exists.
                r"side sidetype, "
                r"price numeric(20,5), "
                r"quantity numeric(20,5), "
                r"type ordertype, "
                r"timestamps timestamp, "
                r"PRIMARY KEY(id), "
                r"FOREIGN KEY(stkid) REFERENCES stocks(id), "
                r"FOREIGN KEY(cfgid) REFERENCES modelconfigs(id) "
            r");" )
        await self.conn.execute(stmt)

        #create table fill history
        stmt = (
            r"CREATE TABLE IF NOT EXISTS fillhistory ( " 
                r"id SERIAL, orderid INT NOT NULL, timestamps timestamp,"
            r");" )

        #        
        stmt = (
            r"CREATE OR REPLACE VIEW orderhistoryview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.name, s.conid, h.cfgid, h.side, h.price, h.quantity, h.type, h.timestamps "
            r"FROM stocks s "
            r"JOIN orderhistory h ON s.id = h.stkid "
            r"ORDER BY s.id, s.conid, h.timestamps DESC;" )
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE OR REPLACE VIEW lateststockpnlview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.name, s.conid, p.realizedpnl, p.timestamps "
            r"FROM stocks s "
            r"JOIN pnls P ON s.id = p.stkid "
            r"ORDER BY s.id, s.conid, p.timestamps DESC;" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE OR REPLACE VIEW latestconfigview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.conid, s.name, c.initvalue, c.leverage, c.statuscode, "
                r"c.numofsinglespread, c.spreadsteppriceratio, c.spreadsteppriceminimal, "
                r"c.timestamps "
            r"FROM stocks s "
            r"JOIN configs c ON s.id = c.stkid "
            r"ORDER BY s.id, s.conid, c.timestamps DESC;" )
        #print(stmt)
        await self.conn.execute(stmt)
        await self.conn.execute("COMMIT;")



    async def getStock(self, stk = True, usedict = True) -> list: 
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE name = $1;", stk )
        elif type(stk)==int:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE conid = $1;", stk )
        elif type(stk)==bool:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values


    async def getConfig(self, stk = None, usedict = True) -> list:
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE name = $1;", stk )
        elif type(stk)==int:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE conid = $1;", stk )
        elif stk == None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values
    

    async def newStock(self, stockname, conid:int = None, exchange = None):
        assert type(conid) == int
        stmt = (
            r"INSERT INTO stocks (name, conid, exchange) "
            r"VALUES ($1, $2, $3);" )
        await self.conn.execute(stmt, stockname, conid, exchange)

    async def delStock(self, conid:int = None):
        assert type(conid) == int
        stmt = r"DELETE FROM stocks WHERE conid = $1;"
        await self.conn.execute(stmt, conid)


    async def updateStockDataByName(self, stkname:str, conid:int, exchange:str):
        assert type(conid) == int
        stmt = (
            r"UPDATE stocks "
            r"SET conid = $1, exchange = $2"
            r"WHERE name = $3;" )
        await self.conn.execute(stmt, conid, exchange, stkname)


    async def updateStockDataByConid(self, conid:int, stkname:str, exchange:str):
        assert type(conid) == int
        stmt = (
            r"UPDATE stocks "
            r"SET name = $1, exchange = $2"
            r"WHERE conid = $3;" )
        await self.conn.execute(stmt, stkname, exchange, conid)


    async def getPnL(self, stk = None, usedict = True):
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE name = $1;", stk)
        elif type(stk)==int:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE conid = $1;", stk)
        elif stk==None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values


    async def getOrderHistory(self, stk = None, todayonly=False, usedict = True):
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE name = $1;", stk)
        elif type(stk)==int:
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE conid = $1;", stk)
        elif stk==None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE True;")
        else:
            raise AssertionError 
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values


    async def checkConfigUpdates(self):
        #if found config's statuscode is new
        #find corresponding status code if there is one
        new_cfgid = None
        return new_cfgid

    async def transportToNewConfigs(self, deprecated_cfgid, new_cfgid):
        #if deprecated_cfgid is not None
            #set deprecated config :final to corresponding pnl :realizedpnl
            #set deprecated config :statuscode -> obsolete
        #create new pnl and set :realizedpnl -> 0
        #set new config :statuscode -> active
        pass

botDB = Database()

class DataBroker():

    def __init__(self):
        self.dbreq = JSONMessenger(name="dbrequest.dbbroker", exchange="db.exchange", routing_key = "db.request")
        self.dbresp = JSONMessenger(name="dbresponse.dbbroker", exchange="db.exchange", routing_key = "db.response")
        self.system = JSONMessenger(name = "sysmsgr.dbbroker", exchange_name = "sys.exchange", routing_key = "sys.message")
        self.exit = False

    async def onSysMessage(self, message):
        if message.get("system") == "exit":
            print("DataBroker receive Exit Message")
            self.exit = True  

    async def start(self):
        try:
            await self.dbreq.connect()
            await self.dbresp.connect()
            self.system.on_message = self.onSysMessage()
            await self.system.connect()
            while(not self.exit):
                await asyncio.sleep(0.1)
        finally:
            await self.dbreq.close()
            await self.dbresp.close()
            await self.system.close()
        

    async def onMessage(self, message):
        key = message.get("msgtype")
        assert key in vars(message)
        await vars(message)[key](self, message[key])

    #save fill data
    async def fill(self, message):
        #retrieve today's fill from database
        #retrieve today's fill from ibkr
        #comparison and find ibkr's fill that are not in database
        #insert fill data into database
        pass

    #save order data
    async def order(Self, message):
        #retrieve today's order from database
        #retrieve today's order from ibkr
        #comparison and find ibkr's order that are not in database
        #insert order data into database
        pass

    #save bot action like place orders modify orders etc.
    async def bot(self, message):
        #message.action = place order
        
        pass

    #CRUD stock datas # because user may be wrong or ibkr may update the stock data
    async def stock(self, message):
        #action = create
        #=> 
        pass

    #Create config datas
    async def config(self, message):
        #action = create
        #=> create => clean pnl set realizedpnl to last and use new config 
        pass

    #CRUD PnL datas
    async def PnL(self, message):
        pass


    
    
    

    