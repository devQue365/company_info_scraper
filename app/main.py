from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from app.schemas import InfoRequest
from app.scraper import *
from app.utils import clean_text
from yfinance import Ticker
import matplotlib.pyplot as plt
# salary module
from app.salary import *
# location module
from app.location import *
# tweets module
from app.tweets import *
# overview module
from app.overview import *
# database module
from app.database import init_db, sessionLocal, start_db_session
from sqlalchemy.orm import Session
from app.leaf import tweet_init_leaf, map_init_leaf, salary_init_leaf, overview_init_leaf
# API usage scheme
from app.api_usage_scheme import get_providers

# Ensure that db is ready ...
init_db()

# Helper function
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print('\033[32m\033[1mSession started ...\033[0m')
    with next(start_db_session()) as db:
        tweet_init_leaf(db) # To initialize the tweet leaf
        map_init_leaf(db) # T initialize the map leaf
        salary_init_leaf(db) # To initialize the salary leaf
        overview_init_leaf(db) # To initialize the overview leaf
    yield
    print('\033[31m\033[1mSession ended ...\033[0m')
# Create the FastAPI app instance
app = FastAPI(lifespan = app_lifespan)
# dependency injection to get database session everytime for every request

# Use : start_db_session()

@app.get("/")
def welcome_msg():
    return {
        'message': 'Welcome to the Company_Info_Scraper V-1.0 API!',
        'explore': {
            'endpoint_1': './get-active-providers',
            'endpoint_2': './docs'
        }
    }
# Endpoint to get active api providers
@app.get('/get-active-providers')
def get_active_api(db : Session = Depends(start_db_session)):
    # here, we are getting a DB session by calling start_db_session() automatically [dependency injection 'Depend'].
    active_providers = get_providers(db) # get active providers list
    print(active_providers)
    if not active_providers: # All exhausted
        raise HTTPException(status_code=429, detail='All the providers have reached their maximum limit.')
    return {
        "active_providers": active_providers
    }

# endpoint to get company information
@app.get('/company-info')
def company_info(request : InfoRequest, db : Session = Depends(start_db_session)):
    # get the active provider
    active_providers = get_providers(db) # get active providers
    # ------- Ticker and About section -------
    ticker = extract_ticker(request.company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    about = extract_about(request.company_name)
    
    # ------- Stocks section -------
    stock = extract_stock_data(t_object)    
   
    # ------- News section -------
    news = extract_news(request.company_name)
   
    # ------- overview section -------
    if(overview_list):
        company_overview = overview_list
    else:
        provider = next((p for p in active_providers if p.token_id == 'ovr'), None)
        if provider:
            # company_overview = ov__1(request.company_name)
            company_overview = "fetching overview ..." # dummy statement
            # check for errors
            if('error' not in company_overview):
                provider.used_calls += 1
        else:
            raise HTTPException(status_code=429, detail='Too many requests ...')

    # ------- Tweets section -------
    provider = next((p for p in active_providers if p.token_id == 'twt'), None)
    if provider:
        fmap_ref = globals()[provider.name]
        # tweets = fmap_ref(request.company_name)
        tweets = "fetchimg tweets ..." # dummy statement
        if 'error' not in tweets:
            provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')
    
    # ------- Location section -------
    provider = next((p for p in active_providers if p.token_id == 'map'), None)
    if provider:
        fmap_ref = globals()[provider.name]
        # locations = fmap_ref(request.company_name, request.location)
        locations = "fetching locations ..." # dummy statement
        # look for errors
        if 'error' not in locations:
            provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')    

    # ------- Salary section -------
    provider = next((p for p in active_providers if p.token_id == 'sal'), None)
    if provider:
        # fmap_ref = globals()[provider.provider]
        salary = glassdoor__v1(request.company_name, request.job_title, request.location, db) 
        # look for errors
        # if 'error' not in salary:
            # provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')
    
    # ------ Update the database -------
    db.commit()
    return {
        "ticker": ticker,
        "about": about,
        'company_overview': company_overview, # (costly)
        "locations": locations,
        "salary": salary,
        "stock_summary": stock.tail(5).to_dict(),
        'latest_ceo_handles': tweets,
        "news": news,
    }