import aiohttp
import asyncio

async def is_proxy_valid(proxy: str, test_url="http://httpbin.org/ip", timeout=10) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, proxy=f"http://{proxy}", timeout=timeout) as resp:
                return resp.status == 200
    except Exception:
        return False

async def get_valid_proxies_from_file(file_path: str, max_concurrent=100) -> list:
    valid_proxies = []
    sem = asyncio.Semaphore(max_concurrent)  # Limit concurrent checks

    async def check(proxy):
        async with sem:
            if await is_proxy_valid(proxy):
                valid_proxies.append(proxy)

    with open(file_path, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]

    await asyncio.gather(*(check(proxy) for proxy in proxies))
    return valid_proxies

# Example usage
if __name__ == "__main__":
    import sys

    file_path = "proxy_list.txt"  # Replace with your actual file path

    async def main():
        valid = await get_valid_proxies_from_file(file_path)
        print(f"Valid proxies ({len(valid)}):")
        for proxy in valid:
            print(proxy)

    asyncio.run(main())
