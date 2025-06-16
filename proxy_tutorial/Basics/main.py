# The problem is that a lot of the proxies will not respond at all while some of them will respond with some error code. So, we nned to filter the proxy list
import requests

with open("valid_proxies.txt", "r") as fh:
    proxies = fh.read().split("\n")

sites_to_check =[ 'https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html',
                 'https://books.toscrape.com/catalogue/category/books/classics_6/index.html',
                 'https://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html']

# mantain a counter
counter = 0
for site in sites_to_check:
    try:
        print(f"Using the proxy : {proxies[counter]}")
        res = requests.get(site, proxies = {
            "http": proxies[counter],
            "https": proxies[counter]
        })
        print(res.status_code)
    except:
        print("Failed")
    finally:
        counter+=1
        # rotate proxies
        counter%(len(proxies))