import requests
import csv
import random
# from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import aiohttp
import asyncio
from asyncio import CancelledError
from contextlib import suppress


# User Agent object
ua= UserAgent()

def get_proxies(file_path: __file__):
    proxy_collection = []
    try:
        with open(file_path, newline='') as csv_file:
            # create reader object
            reader = csv.DictReader(csv_file)
            for row in reader:
                if all(k in ('Host', 'Port', 'User', 'Pass') for k in row):
                    # generate proxy record
                    proxy_record = {
                        'host': row['Host'].strip(),
                        'port': row['Port'].strip(),
                        'user': row['User'].strip(),
                        'pass': row['Pass'].strip()
                    }
                    # get the url -> https://username:password:host:port
                    proxy_url = f"http://{proxy_record['user']}:{proxy_record['pass']}@{proxy_record['host']}:{proxy_record['port']}"
                    # proxy_url = f"http://{proxy_record['host']}:{proxy_record['port']}"

                    proxy_collection.append(proxy_url)
        return proxy_collection
    except Exception as e:
        return {'error': str(e)}


def check_proxies__v1(proxy_pool):
    # shuffle the proxy pool
    random.shuffle(proxy_pool)
    # always get a random user agent
    # get the header
    headers = {
        'User-Agent': ua.random
    }
    while(proxy_pool):
        # pop a proxy
        proxy = proxy_pool.pop()
        try:
            # make requests
            response = requests.get("http://ipinfo.io/json", headers=headers, proxies = {
                'http': proxy,
                'https': proxy
            })
        except Exception as e:
            continue
        # if successful
        if(response.status_code == 200):
            return proxy
    return "No proxy is working !"


async def check_proxies__v2(proxy):
    # test url
    test_url = 'http://ipinfo.io/json'
    # get header with random user agent
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent
    }
    try:
        # create an asynchronous session
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, proxy = proxy, timeout = 10, headers = headers) as res:
                if (res.status == 200):
                    print("Proxy worked !!!!")
                    return (user_agent, proxy)
                else:
                    print("Proxy did not work !!!!")
                    return None
    except Exception as e:
        print(f"Exception : {str(e)}")
        return None
    
    
async def get_proxy_after_rotation(proxypool):
    # run all the proxies in parallel i.e. concurrent way
    jobs = [asyncio.create_task(check_proxies__v2(proxy)) for proxy in proxypool]
    # check status of proxies
    done, pending = await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
    # for the proxy which got selected
    selected_proxy = None
    # check the done segment
    for job in done:
        result = job.result()
        if result:
            selected_proxy = result
            break # no need to check further
    # terminate the pending jobs
    for job in pending:
        job.cancel()
        with suppress(CancelledError):
            await job     
    # check if no proxy is selected i.e. all are out of service
    if not selected_proxy:
        print("None of the proxy is in working state ...")
        return None
    
    return selected_proxy

# simple function
def fetch_proxy(file_name):
    # initialize a proxy pool
    proxypool = get_proxies(file_name)
    # get the proxy
    random.shuffle(proxypool)
    proxy = asyncio.run(get_proxy_after_rotation(proxypool))
    return proxy

