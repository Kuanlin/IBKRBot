

#check bot is running

#check known stocks in database

#check model config model.json 
#check model parameters in database

#check 
import sys
sys.path.append('..') 

import argparse
import asyncio, asyncpg
from ConfigProvider import auths
from pprint import pprint as pp

async def tellbot_run():
    try:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        #new or update config..
        sc = subparsers.add_parser("set-config", aliases = ['sc'], description = r"New or update config")
        sc.set_defaults(act="set_config")
        scgroup = sc.add_mutually_exclusive_group()
        scgroup.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        scgroup.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        sc.add_argument('-lv', '--leverage', 
            help = r"set the leverage", required = True)
        sc.add_argument('-iv', '--initvalue', 
            help = r"set initial value", required = True)
        sc.add_argument('-sc', '--statuscode', choices=[r'new', r'active', r'deprecated', r'obsolete'],
            help = r"set status code", required = True)
        sc.add_argument('-ns', '--numofspread', 
            help = r"set the number of single side orders to be spread", required = True)   
        sc.add_argument('-sr', '--spreadsteppriceratio', 
            help =r"set the price step ratio for orders <1: the further the smaller >1: the further the larger =0: use minimal value", required = True)
        sc.add_argument('-sm', '--spreadsteppriceminimal',
            help =r"set the minimum price step for orders", required = True)
        
        #list config
        lc = subparsers.add_parser("list-config", aliases = ['lc'], description = r"List configs")
        lc.set_defaults(act='list_config')
        lcgroup = lc.add_mutually_exclusive_group()
        lcgroup.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        lcgroup.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        lcgroup.add_argument('-a', '--all', action='store_true',
            help = r"list all configurations")
        lc.add_argument('-sc', '--statuscode', choices=[r'stop', r'active', r'liquiding', r'deprecated'],
            help = r"filter by status code -- default = active", required = True, default = r'active')

        #add stock data
        ast = subparsers.add_parser("add-stock", aliases = ['stk'], description = r"Add Stock Data")
        ast.set_defaults(act="add_stock")
        ast.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        ast.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        ast.add_argument('-e', '--exchange',
            help = r"provide stock's exchange" , type = str)

        #list stock data
        lstk = subparsers.add_parser("list-stock", aliases = ['lst'], description = r"List Stock Data")
        lstk.set_defaults(act="list_stock")
        lstkgroup = lstk.add_mutually_exclusive_group()
        lstkgroup.add_argument('-a', '--all', action='store_true', help = r"list all stock data")
        lstkgroup.add_argument('-act', '--active', action='store_true', help = r"list all actived stock data")

        #list PnL
        lpnl = subparsers.add_parser("list-pnl", aliases = ['pnl'], description = r"List PnL Data")
        lpnl.set_defaults(act="list_pnl")
        lpnlgroup = lpnl.add_mutually_exclusive_group()
        lpnlgroup.add_argument('-a', '--all', action='store_true', help = r"list all PnL data")
        lpnlgroup.add_argument('-act', '--active', action='store_true', help = r"list all actived PnL data")

        try:
            args = parser.parse_args()
            f = (globals()[args.act])
            await f(args)

        except SystemExit:
            pass
        return 0
    
    except Exception as err:
        import traceback
        tb = traceback.format_exc()
        print(tb)


async def set_config(args):
    
    #find all configs that match the same conid, and statuscode is new or active
    #set config new -> obsolete
    #set config active -> deprecated

    print('set_config')

    print(args)


async def list_config(args):
    print('list_config')
    print(args)

async def add_stock(args):
    print('add_stock')
    print(args)

async def list_stock(args):
    print('list_stock')
    print(args)

async def list_pnl(args):
    print('list_pnl')
    print(args)

async def tellbot():
    try:
        await asyncio.gather( bset_run() )
    except:
        import traceback
        tb = traceback.format_exc()
        #print(tb)
    loop = asyncio.get_event_loop()
    loop.stop()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(tellbot())
    loop.run_forever()

if __name__ == '__main__':
    import docker
    client = docker.from_env()
    for i in ["ibkr", "rmq", "pdb"]:
        c = client.container.get(i)
        if not c.status == "running":
            print(f"Aborted #{i} is not running.")
            exit()
    run()
