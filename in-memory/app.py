import json
import time
import atexit
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

app = Flask(__name__)

class ProxyService:
    def __init__(self, proxy):
        self.data = {}
        if os.path.exists('data.json'):
            with open('data.json', 'r') as fp:
                self.data = json.load(fp)
                self.data = {int(k): self.data[k] for k in self.data}
        else:
            for proxy in proxies:
                for resource_id in proxy['resource_ids']:
                    if resource_id not in self.data:
                        self.data[resource_id] = {'free': [], 'busy': {}}
                    self.data[resource_id]['free'].append(proxy.copy())
                
    def backup(self):
        with open('data.json', 'w') as fp:
            json.dump(self.data, fp)
            # print('data saved to disk')
            
    def free_proxy(self):
        for resource in self.data:
            now = time.time()
            busylist = self.data[resource]['busy'].copy()
            for busy in busylist:
                if self.data[resource]['busy'][busy]['ttl'] < now:
                    self.data[resource]['free'].append(self.data[resource]['busy'][busy])
                    self.data[resource]['busy'].pop(busy)
    
    def allocate_proxy(self,resource,ttl,country):
        self.free_proxy()
        if self.data.get(resource):
            free = self.data[resource].get('free')
            if free:
                for busy in free:
                    if busy['country'] == country or country == '':
                        self.data[resource]['free'].remove(busy)
                        busy['ttl'] = time.time() + ttl;
                        busy['rpw'] += 1
                        self.data[resource]['busy'][busy['address']] = busy
                        return busy
                return 'no such proxy with selected country and resource'
            else: 
                return 'no free proxies for service'
        return 'no proxies for resource ' + resource
    
    
# proxies = [
#     {'address': 'proxy1.com', 'country': 'USA', 'rpw': 100, 'resource_ids': [1, 2, 3]},
#     {'address': 'proxy2.com', 'country': 'Canada', 'rpw': 50, 'resource_ids': [2, 3]},
#     {'address': 'proxy3.com', 'country': 'USA', 'rpw': 200, 'resource_ids': [1]},
#     {'address': 'proxy4.com', 'country': 'Canada', 'rpw': 150, 'resource_ids': [1, 2]},
# ]

proxies = []
with open('proxy_list.json', 'r') as fp:
    proxies = json.load(fp)

service = ProxyService(proxies)

scheduler = BackgroundScheduler()
scheduler.add_job(func=service.backup, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/allocate/<proc_id>/<ttl>/<country>")
def allocate(proc_id,ttl,country):
    return service.allocate_proxy(int(proc_id),int(ttl),country)

@app.route("/allocate/<proc_id>/<ttl>")
def allocate_no_country(proc_id,ttl):
    return service.allocate_proxy(int(proc_id),int(ttl),'')
