import asyncio, asyncpg
from ConfigProvider import auths

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
        stmt = (
            r"SELECT datname FROM pg_catalog.pg_database WHERE datname = $1;"
        )
        result = await self.conn.fetch(stmt, DATABASE)
        if (len(result)==0):
            await self.conn.execute(f"CREATE DATABASE {DATABASE}")
        self.conn = await asyncpg.connect(
            user=ACCOUNT, password=PASSWORD,
            database=DATABASE, host='127.0.0.1')
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status') THEN "
                    r"CREATE TYPE status AS ENUM ('stop', 'active', 'liquidating', 'deprecated');"
                r"END IF;"
            r"END $$;" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE TABLE IF NOT EXISTS stocks ("
                r"id SERIAL, conid INT, "
                r"name Varchar(255),"
                r"exchange Varchar(255), timestamps timestamp,"
                r"PRIMARY KEY(id)"
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)
        
        stmt = (
            r"CREATE TABLE IF NOT EXISTS configs ( "
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

        stmt = (
            r"CREATE TABLE IF NOT EXISTS pnls ( "
                r"id SERIAL, stkid INT NOT NULL, cfgid INT NOT NULL, "
                r"realizedpnl numeric(20,5), timestamps timestamp, "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ), "
                r"FOREIGN KEY(cfgid) REFERENCES configs(id), "
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sidetype') THEN "
                    r"CREATE TYPE sidetype AS ENUM ('BUY', 'SELL');"
                r"END IF;"
            r"END $$;" )
        await self.conn.execute(stmt)

        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ordertype') THEN "
                    r"CREATE TYPE ordertype AS ENUM ('LMT', 'MKT');"
                r"END IF;"
            r"END $$;" ) 
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE TABLE IF NOT EXISTS OrderHistory ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"cfgid INT NOT NULL, "
                r"side sidetype, "
                r"price numeric(20,5), "
                r"quantity numeric(20,5), "
                r"type ordertype, "
                r"timestamps timestamp, "
                r"PRIMARY KEY(id), "
                r"FOREIGN KEY(stkid) REFERENCES stocks(id), "
                r"FOREIGN KEY(cfgid) REFERENCES configs(id) "
            r");" )
        await self.conn.execute(stmt)

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


botDB = BotDB()