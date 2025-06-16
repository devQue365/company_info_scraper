import aiohttp
import asyncio
from fake_useragent import UserAgent
# First of all we will be having a boolean function to check for the validity of the proxies
async def is_proxy_valid(proxy, test_url = "http://httpbin.org/ip", timeout = 10) -> bool:
    try:
        ua = UserAgent()
        user_agent = ua.random
        headers = {
            'User-Agent': user_agent
        }
        # create a client session
        async with aiohttp.ClientSession() as session:
            async with session.get(url=test_url, timeout=timeout, proxy=f"http://{proxy}", headers=headers) as res:
                return res.status == 200
    except:
        return False

# Now, we will be running the main routine
async def getValidProxies(file_name, max_concurrent_processing = 100) -> list:
    valid_proxies = []
    '''A semaphore is like a counter.
    It limits how many coroutines can run at the same time.
    Here, at most max_concurrent proxy checks will run simultaneously.
    Prevents system overload or hitting the server too aggressively.'''
    sem = asyncio.Semaphore(max_concurrent_processing)
    # get a wrapper function
    async def check_proxy(proxy):
        nonlocal valid_proxies
        async with sem:
            if await is_proxy_valid(proxy):
                valid_proxies.append(proxy)
    # read proxies from file
    with open(file_name, "r") as fh:
        proxy_list = [line.strip() for line in fh if line.strip()]
    # run the concurrent tasks
    await asyncio.gather(*(check_proxy(proxy) for proxy in proxy_list))
    with open("valid_proxies.txt", "w") as fh:
        fh.write("\n".join(valid_proxies))
    # return valid_proxies

# async def main():
#     proxies = await getValidProxies('proxy_list.txt')
#     print(proxies)
#     print(len(proxies))
# if __name__ == '__main__':
#     asyncio.run(main())