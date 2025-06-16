# pip3 install aiohttp
import aiohttp
import asyncio

# define a timeout in seconds
time_out = 10

# test URL
url = "https://httpbin.io/ip"

# specify the proxies file
proxy_file = "proxy_list.txt"



# validate a single proxy
async def check_proxy(url, proxy):
    try:
        # create an aiohttp session
        session_timeout = aiohttp.ClientTimeout(
            total=None, sock_connect=time_out, sock_read=time_out
        )

        # visit the target site asynchronously with proxy
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            async with session.get(
                url, proxy=f"http://{proxy}", timeout=time_out
            ) as response:
                print(await response.text())
    except Exception as error:
        print("Proxy responded with an error: ", error)
        return


# main function to read and validate proxies
async def main():
    tasks = []
    # read the proxies from the proxy list file
    proxies = open(proxy_file, "r").read().strip().split("\n")

    # run the task concurrently
    for proxy in proxies:
        task = asyncio.create_task(check_proxy(url, proxy))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # execute the main function
    asyncio.run(main())
