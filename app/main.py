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
@app.post('/company-info')
def company_info(request : InfoRequest, db : Session = Depends(start_db_session)):
    # get the active provider
    # active_provider = select_provider(db) # get active provider
    # if not active_provider: # All exhausted
        
        # salary = extract_salary(request.company_name,request.job_title)
    
    # now check for each level of API provider
    # def getSalaryData():
    #     nonlocal db
    #     nonlocal request
    #     # get list of providers
    #     active_providers = active_provider_list(db)
    #     # if no active provider
    #     if not active_providers:
    #         raise HTTPException(status_code=429, detail='All the APIs have reached their maximum limit.')
        # for provider in active_providers:
        #     if(provider.provider == 'jsearch'):
        #         salary = jsearch(request.company_name, request.job_title,request.location)
        #     elif(provider.provider == 'glassdoor'):
        #         salary = glassDoor(request.company_name, request.job_title,request.location)
        #     elif(provider.provider == 'jobsalarydata'):
        #         salary = job_salary_data_api(request.company_name, request.job_title, request.location)
        #     elif(provider.provider == 'careerjet'):
        #         salary = carrer_jet_api(request.company_name, request.job_title, request.location)

            # Analyze API response
            # if 'error' not in salary:
            #     provider.used_calls+=1
            #     db.commit()
            #     return salary
        # return salary
    # provider = active_provider_list(db)[2]
    # salary = glassDoor__v2(request.company_name, request.job_title, request.location)
    # if 'error' not in salary:
    #     provider.used_calls+=1
    #     db.commit()
    # Going for each section's relational schema

    ticker = extract_ticker(request.company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    ''' For company overview, we will use the overview module.
    It will first check if the overview_list is not empty, then it will use the overview_list.
    If it is empty, then it will use the ov__1 function to get the overview of the company.
    '''
    # if(overview_list):
    #     company_overview = overview_list
    # else:
    #     company_overview = ov__1(request.company_name)
    about = extract_about(request.company_name)
    # locations = gm__2(request.company_name, request.location)
    # stock = extract_stock_data(t_object)    
    # tweets = twt__4(request.company_name)
    ''' For news, we will use the extract_news function.'''
    news = extract_news(request.company_name)
    return {
        "ticker": ticker,
        "about": about,
        # 'company_overview': company_overview, # (costly)
        # "locations": locations,
        # "salary": salary,
        # "stock_summary": stock.tail(5).to_dict(),
        # 'latest_handles': tweets,
        "news": news,
    }