import threading
import queue

import requests

# create a queue object
q = queue.Queue()
# Hold valid proxies
valid_proxies = []

# file-handling to read and enqueue the proxies.
with open("proxy_list.txt", "r") as fh:
    proxies = fh.read().split("\n")
    for p in proxies:
        q.put(p)

# function to check for validity of proxies
def check_proxies():
    global q
    while(not q.empty()):
        # perform dequeue operation
        proxy = q.get()
        # make a request using that proxy
        try:
            res = requests.get("http://ipinfo.io/json", 
                            proxies={
                                "http": proxy,
                                "https": proxy
                            })
        except:
            continue
        # valid proxy servers
        if res.status_code == 200:
            valid_proxies.append(proxy)
    return valid_proxies

# run multiple threads
for _ in range(10):
    threading.Thread(target=check_proxies).start()
        
