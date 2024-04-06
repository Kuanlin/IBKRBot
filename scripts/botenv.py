import docker, os, json, string, random
from getpass import getpass

params_env = {
    "ibkr" : {
        "image" : "voyz/ibeam",
        "account_tag" : "IBEAM_ACCOUNT",
        "password_tag" : "IBEAM_PASSWORD",
        "params" : { #voyz/ibeam
            'stdin_open':True,
            'tty':True,
            'detach': True,
            'name' : 'ibkr',
            'ports': {'5000': '5000'},
            'environment': {
                'IBEAM_ACCOUNT' : '',
                'IBEAM_PASSWORD' : '' } } }, 
    "pdb" : {
        "image" : "postgres",
        "account_tag" : "POSTGRES_USER",
        "password_tag" : "POSTGRES_PASSWORD",
        "params" : { #postgres
        'detach': True,
        'name' : 'pdb',
        'ports' : {'5432': '5432'},
        'environment': {
            'POSTGRES_USER': '',
            'POSTGRES_PASSWORD': ''},
        'volumes':{
            '/home/' + os.getlogin() + '/data': {'bind': '/data', 'mode': 'rw'} } } },
    "rmq" : {
        "image" : "rabbitmq",
        "account_tag" : "RABBITMQ_DEFAULT_USER",
        "password_tag" : "RABBITMQ_DEFAULT_PASS", 
        "params" : { #rabbitmq
            'detach': True,
            'name': 'rmq',
            'ports': {'5672': '5672'},
            'environment': {
                'RABBITMQ_DEFAULT_USER': '',
                'RABBITMQ_DEFAULT_PASS': '' } } } }

def create():
    idgen = lambda idlen:"".join([random.choice(string.ascii_letters)] + random.choices(string.ascii_letters+string.digits, k=idlen-1))
    pwdgen = lambda pwdlen: "".join(random.choices(string.ascii_letters+string.digits+string.punctuation, k=pwdlen))
    j = {}
    try:
        f = open("../config/dockconf.json", "r")
        j = json.load(f)
        f.close()
    except FileNotFoundError:
        pass
    config = j
    client = None
    print("getting docker env", flush = True)
    try:
        client = docker.from_env()
    except:
        print("getting docker env failed", flush = True)
        return
    #pull if not exists
    for image_name in [ params_env[x]["image"] for x in params_env ]:
        try:
            print(f"Image name #{image_name} exists.", flush = True)
            client.images.get(image_name)
        except docker.errors.ImageNotFound:
            print(f"Image name #{image_name} not exists.", flush = True)
            print(f"Pull docker name = #{image_name}", flush = True)
            client.images.pull(image_name)

    containers = client.containers.list(all=True)
    name_container_dict = { x.name:x for x in containers }
    
    for c in params_env.keys():
        if c in name_container_dict:
            print(f"Container #{c} exists.", flush = True)
        else: # docker init here
            print(f"Container #{c} not exists.", flush = True)
            if c == "ibkr":
                if not j.get(c):
                    account, password = None, None
                else:
                    account = j.get(c).get("account")
                    password = j.get(c).get("password")
                if not account:
                    while not (account:=input(f"#{c} account:")): pass;
                if not password:
                    while not (password:=getpass(f"#{c} password:")): pass;
            else:
                if not j.get(c):
                    account, password = None, None
                else:
                    account = j.get(c).get("account")
                    password = j.get(c).get("password")
                if not account:
                    account = idgen(8)
                    #while not (account:=input(f"#{c} account:")): pass;
                if not password:
                    password = pwdgen(16)
                    #while not (password:=getpass(f"#{c} password:")): pass;              
                config[c] = { "account" : account, "password" : password }
            params_env[c]["params"]["environment"][ params_env[c]["account_tag"] ] = account
            params_env[c]["params"]["environment"][ params_env[c]["password_tag"] ] = password
            print(f"Run #{c} for the first time.", flush = True)
            client.containers.create( params_env[c]["image"], **(params_env[c]["params"]) )
    with open("init.json", "w") as f:
        f.write(json.dumps(config, indent=4))

def start():
    try:
        client = docker.from_env()
    except:
        print("getting docker env failed", flush = True)
        return
    containers = client.containers.list(all=True)
    name_container_dict = { x.name:x for x in containers }
    for c in params_env.keys():
        print(f"Check Container name #{c}:", end="", flush=True)
        if c not in name_container_dict:
            print("not exists. Abandon", flush=True)
            return
        else:
            print("exists", flush=True)
    for c in params_env.keys():
        print(f"Starting Container name #{c}:", end="", flush=True)
        container = client.containers.get(c)
        container.start()
        container = client.containers.get(c)
        if container.status == "running":
            print("Successed", flush = True)
        else:
            print("Failed", flush = True)


def stop():
    try:
        client = docker.from_env()
    except:
        print("getting docker env failed", flush = True)
        return
    containers = client.containers.list(all=True)
    name_container_dict = { x.name:x for x in containers }
    check_container = []
    for c in params_env.keys():
        print(f"Check Container name #{c}:", end="", flush=True)
        if c not in name_container_dict:
            print("not exists.", flush=True)
        else:
            print("exists", flush=True)
            check_container.append(c)
    for c in check_container:
        print(f"Stopping Container name #{c}:", end="", flush=True)
        container = client.containers.get(c)
        container.stop()
        container.reload()
        if container.status == "exited":
            print("Successed", flush = True)
        else:
            print("Failed", flush = True)


def removecontainers():
    try:
        client = docker.from_env()
    except:
        print("getting docker env failed")
        return
    for name in params_env.keys():
        try:
            container = client.containers.get(name)
            container.remove()
            try:
                client.containers.get(name)
                print(f"Container name #{name} may not removed.", flush = True)
            except:
                print(f"Container name #{name} removed.", flush = True)
        except docker.errors.APIError:
            print(f"Unable to delete container name #{name}. Is it still running?", flush = True)
        except docker.errors.NotFound:
            print(f"Container name #{name} not exists.", flush = True)


def removeimages():
    try:
        client = docker.from_env()
    except:
        print("getting docker env failed")
        return
    image_names = [ params_env[x]["image"] for x in params_env.keys() ]
    for name in image_names:
        try:
            image = client.images.get(name)
            image.remove()
            try:
                client.images.get(name)
                print(f"Image name #{name} may not removed.", flush = True)
            except:
                print(f"Image name #{name} removed.", flush = True)
        except docker.errors.APIError:
            print(f"Unable to delete image name #{name}. Is it still running?", flush = True)
        except docker.errors.NotFound:
            print(f"Image name #{name} not exists.", flush = True)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.set_defaults(act="ctl")

    xg = parser.add_mutually_exclusive_group()
    xg.add_argument("-c", "--create", action="store_true", help = r"Create")
    xg.add_argument("-s", "--start", action="store_true", help = r"Start")
    xg.add_argument("-q", "--stop", action="store_true", help = r"Stop")
    xg.add_argument("-xc", "--removecontainers", action="store_true", help = r"Remove all containers")
    xg.add_argument("-xi", "--removeimages", action="store_true", help = r"Remove all images")

    args = parser.parse_args()
    try:
        choice = [ k for k, v in (vars(args)).items() if v == True ][0]
    except:
        parser.print_help()
    globals()[choice]()
