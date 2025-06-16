import requests
import yfinance as yf
from tabulate import tabulate
import pandas as pd
import csv
import feedparser
from newspaper import Article
import time
from difflib import SequenceMatcher
# main scraping libraries / modules
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
# from app.Parser import customizedParser
import urllib.parse
mock_header = {
        "User-Agent": "Mozilla/5.0"
    }

def extract_about(company_name):
    try:
        # First of all request data from yfinance API
        # create a ticker object
        ticker = extract_ticker(company_name)
        t_object = yf.Ticker(ticker)
        # get company's information
        information = t_object.info
        # request company's longBusinessSummary
        if 'longBusinessSummary' in information:
            business_summary = information['longBusinessSummary']
            return business_summary
        options = uc.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        # if(headless):
        options.add_argument("--headless=new")
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
        driver = webdriver.Chrome(options = options)
        # sanitize the query
        company_name+=' company'
        company_name = company_name.replace('+',' plus ').replace('-',' minus ')
        url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}"
        # url = f"https://www.google.com/search?q={company}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 5)
        # wiki_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='Q7PwXb a-no-hover-decoration ztWovc']")))
        wiki_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='y171A Q7PwXb a-no-hover-decoration' or @class='Q7PwXb a-no-hover-decoration ztWovc']")))
        wiki_link.click()
        # wait for sometime
        time.sleep(5)
        wiki_src = driver.page_source
        soup = BeautifulSoup(wiki_src, 'html.parser')
        # select paragraph tag
        p = soup.select('p')
        for each_para in p:
            # select only valuable text
            if(len(each_para.text.strip()) > 150):
                return each_para.text.strip()
    except Exception as e:
        return None
    
def extract_salary(company_name, job_title):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options)
    url = f"https://www.levels.fyi/companies/{company_name}/salaries/{job_title.replace(' ','-')}"
    driver.get(url)
    driver.maximize_window()
    
    try:
        # Wait for the clickable button
        wait = WebDriverWait(driver, 10)
        view_more_levels = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textNeutral MuiButton-sizeLarge MuiButton-textSizeLarge MuiButton-colorNeutral MuiButton-root MuiButton-text MuiButton-textNeutral MuiButton-sizeLarge MuiButton-textSizeLarge MuiButton-colorNeutral css-y5b368']")))
        view_more_levels.click()
        print('clicked sir')
        time.sleep(2)
    except Exception as e:
        pass
    # get the raw html
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    driver.close()
    # get the table
    table = soup.find('table', class_ = 'MuiTable-root css-1f6fkxk')
    if not table:
        return None
    # print('table found')
    result = []
    # find tbody
    try:
        tbody = table.find('tbody', class_ = 'MuiTableBody-root job-family_tableBody__MaiIw css-1xnox0e')
        if not tbody:
            return None
        # print('found tbody')
        # find all rows
        rows = tbody.find_all('tr', class_ = 'MuiTableRow-root job-family_bodyRow__WuAug css-140sacz')
        # traver each row
        for row in rows:
            # get columns as td value
            col = row.find_all('td', class_ = 'MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft MuiTableCell-sizeMedium css-k1mugk')
            # we want minimum results
            if len(col) >= 5:
                salary_record = {
                    'level': col[0].get_text(strip = True),
                    'Total': col[1].get_text(strip = True),
                    'Base': col[2].get_text(strip = True),
                    'Stock (/yr)': col[3].get_text(strip = True),
                    'Bonus': col[4].get_text(strip = True)
                }
                result.append(salary_record)
        return result
    except Exception as e:
        return None
def extract_ticker(company_name):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
    mock_header = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers = mock_header)
    results = response.json().get("quotes", [])
    for result in results:
        if "symbol" in result and "shortname" in result:
            return result["symbol"]
    return None





def extract_stock_data(t_object, period = '1d'): 
    # fetch data accoding to your need
    data = t_object.history(period = period)
    return data

def extract_news(company_name):
    # Pass RSS url
    url = f"https://news.google.com/rss/search?q={company_name}+company+latest+insights"
    # Get the feed
    feed = feedparser.parse(url)
    if feed.bozo == True:
        # print('Error extracting news')
        return None
    # print(f'\033[1m\033[33m{len(feed.entries)} entries found !\033[0m')
    container = []
    # Examine each entry
    for entry in feed.entries[:5]:
        data = []
        # Get the title
        data.append(entry.title)
        data.append(entry.published if 'published' in entry else 'Unknown')
        data.append(entry.author if 'author' in entry else 'Unknown')
        # data.append(entry.summary if 'summary' in entry else None)
        data.append(entry.link)
        # Create newspaper object
        article = Article(entry.link)
        # download the article
        article.download()
        article.parse()
        # Get the text
        data.append(article.text[:300])
        # Add to the main container
        container.append(data)
    return container

def extract_reviews(company_name, job_title):
    try:
        ua = UserAgent()
        user_agent = ua.random
        options = uc.ChromeOptions()
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        # if(headless):
        # options.add_argument("--headless=new")
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3") 
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_argument("--disable-background-timer-throttling")
        # options.add_argument("--disable-backgrounding-occluded-windows") 
        # options.add_argument("--disable-renderer-backgrounding")  
        # options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        driver = webdriver.Chrome(options = options)
        # Get the query params
        query_params = {
            "q": f"site:glassdoor.com \"reviews\" {company_name} {job_title}"
        }
        # keywords
        keywords = f"{company_name} {job_title}".split()
        url_safe_query = urllib.parse.urlencode(query_params)
        url = f"https://www.google.com/search?{url_safe_query}"
        driver.get(url)
        def not_a_bot(driver):
            wait = WebDriverWait(driver, 15)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@name,'a-') and starts-with (@src, 'https://www.google.com/recaptcha')]")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='recaptcha-checkbox-border']"))).click()
            driver.switch_to.default_content()
        not_a_bot(driver)
        # get the main links container
        link_container = driver.find_element(By.CLASS_NAME, "dURPMd")
        # explore all the link cards
        link_cards = link_container.find_elements(By.CLASS_NAME, "MjjYud")
        # now explore each of the link cards
        for card in link_cards:
            # get the span section
            try:
                # check whether we are making correct choice 
                h3_title = card.find_element(By.CLASS_NAME, "LC20lb MBeuO DKV0Md").text
                provider = card.find_element(By.CLASS_NAME, "VuuXrf").text
                ## check for provider (security)
                if(provider.lower() == 'glassdoor'):
                    ## check availability of keywords (security)
                    # for k in keywords:
                    #     if k not in h3_title:
                    #         continue
                    span_section = card.find_element(By.TAG_NAME, "span")
                    if span_section:
                        anchor = card.find_element(By.CLASS_NAME, "zReHs")
                        anchor.click()
                        # wait for some time to mimic real browser
                        time.sleep(3)
                        # get the page source
                        page_source = driver.page_source
                        break
            except:
                continue
            # Now, we are working on glassdoor site
            ## from here we will be using beautiful soup
            soup = BeautifulSoup(page_source, 'html.parser')
            feed = soup.find("div", id="ReviewsFeed")
            ## get the ordered list
            ol = feed.find("ol", class_ = "ReviewsList_reviewsList__Qfw6M")
            ## extract upper section credentials - ceo, ceo_approval, recommend_line
            u_section = soup.find("div", class_ = "module-container_moduleContainer__tpBfv module-container_redesignContainer__rLCJ4")
            # get recommend_line
            recommend_line = u_section.find("p", class_ = "review-overview_recommendLine__ecVgo").text
            # get ceo name
            ceo_name = u_section.find("p", class_ = "review-overview_ceoName__8AcsH").text
            # get ceo approval
            ceo_approval = u_section.find("p", class_ = "review-overview_ceoApproval__oy27U").text
            ## explore individual review cards
            review_container = []
            _ctr = 0
            for li in ol:
                try:
                    # get the top container - date, review rating
                    rating = li.find("span", class_ = "review-rating_ratingLabel__0_Hk9").text
                    date_posted = li.find("span", class_ = "timestamp_reviewDate__dsF9n").text
                    # go to the header container of the li card
                    header = li.find("div", class_ = "review-details_headerContainer__ctBF6")
                    ## extract individual elements - review_title, job_role, current_status
                    r_title = header.find("h3",class_ = "heading_Heading__BqX5J heading_Level3__X81KK").text
                    r_job_role = header.find("span", class_ = "review-avatar_avatarLabel__P15ey").text
                    # for current status and location
                    sub_header = header.find_all("div", class_ = "text-with-icon_LabelContainer__xbtB8 text-with-icon_disableTruncationMobile__o_kha")
                    r_current_status = sub_header[0].text
                    r_location = sub_header[1].text
                    # get pros
                    r_pros = li.find("span", {"data-test": "review-text-PROS"}).text
                    r_cons = li.find("span", {"data-test": "review-text-CONS"}).text
                    record = {
                        'rating': rating,
                        'date_posted': date_posted,
                        'review_title': r_title,
                        'reviewer_job_role': r_job_role,
                        'reviewer_current_status': r_current_status,
                        'location': r_location,
                        'reviews': {
                            'pros': r_pros,
                            'cons': r_cons
                        }
                    }
                    _ctr+=1
                    review_container.append(record)
                except Exception as e:
                    continue
        return {
            'ceo_name': ceo_name,
            'ceo_approval': ceo_approval,
            'recommend_line': recommend_line,
            'reviews': review_container
        }
    except Exception as e:
        return {"error": "No review information available ..."}
    

# print(extract_reviews('apple', 'software engineer')) 