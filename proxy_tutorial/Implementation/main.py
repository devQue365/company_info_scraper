import asyncio
import random
from validate import getValidProxies
from fake_useragent import UserAgent
# Selenium tools
from seleniumwire import webdriver as wiredriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import ProtocolError


# load the proxies
# asyncio.run(getValidProxies('proxy_list.txt'))


# Implemented the proxy rotation logic and fake user agents
## Create fake user agent object
ua = UserAgent()
## get the proxy list
print("Selecting a random proxy ...")
with open("valid_proxies.txt", "r") as fh:
    proxies = [line.strip() for line in fh if line.strip()]
print("Got the proxy ...")
print(proxies)
retries = 3
for _ in range(2):
    proxy = random.choice(proxies) # for proxy
    user_agent = ua.random # for user agent
    proxy_options = {
        'http': f"http://{proxy}",
        'https': f"https://{proxy}"
    }
    try:
        options = Options()
        # options.add_argument("--headless")
        options.add_argument(f"user-agent={user_agent}")
        # if(headless):
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows") 
        options.add_argument("--disable-renderer-backgrounding")  
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        # set up a driver instance
        driver = wiredriver.Chrome(
            service = ChromeService(ChromeDriverManager().install()),
            chrome_options = options,
            seleniumwire_options={"proxy": proxy_options},
        )
        # show the details
        print(f"\033[32m\033[1mUsing Proxy: {proxy}")
        print(f"\033[34mUsing User-Agent: {user_agent}\033[0m")
        # Visit a test site to verify the proxy connection
        driver.get("https://www.google.com/search?q=site%3Aglassdoor.com+%22reviews%22+apple+software+engineer")
        WebDriverWait(driver, 10)
        # driver.get("http://httpbin.org/ip")
        # res = driver.find_element(By.TAG_NAME, "body").text
        # print(res)
        # driver.quit()
        break
    except (TimeoutException, ProtocolError) as e:
        print(f"\033[31m\033[1mError: {str(e)}\033[0m")
        retries-=1
        print(f"Retries left: {retries}")
        if retries == 0:
            print("Maximum retries reached. Exting ....")
            break
        print("Retrying with a different proxy...")
    finally:
        # Ensure the driver is closed even if an exception occurs
        if "driver" in locals():
            driver.quit()