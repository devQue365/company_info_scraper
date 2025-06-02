from fastapi import FastAPI, Depends, HTTPException
from app.schemas import InfoRequest
from app.scraper import *
from app.utils import clean_text
from yfinance import Ticker
import matplotlib.pyplot as plt
# salary module
from app.salary import *
# location module
from app.location import *
# database module
from app.database import init_db, sessionLocal, start_db_session
from sqlalchemy.orm import Session
# API usage scheme
from app.api_usage_scheme import select_provider, active_provider_list
app = FastAPI()
# ensure that db is ready ...
init_db()

# dependency injection to get database session everytime for every request
# Use : start_db_session()

@app.get("/")
def welcome_msg():
    return {'message': 'Welcome to the scraping API !!',
            'endpoint-1': './get-active-api'}

# endpoint to get active api
@app.get('/get-active-api')
def get_active_api(db : Session = Depends(start_db_session)):
    # here, we are getting a DB session by calling start_db_session() automatically [dependency injection 'Depend'].
    active_provider = select_provider(db) # get active provider
    if not active_provider: # All exhausted
        raise HTTPException(status_code=429, detail='ALl the APIs have reached their maximum limit.')
    return {
        'provider' : active_provider.provider,
        'used_calls' : active_provider.used_calls,
        'total_calls' : active_provider.total_calls,
        'reset-type' : active_provider.reset_type,
        'last_reset' : active_provider.last_reset
    }

# endpoint to get company information
@app.post('/company-info')
def company_info(request : InfoRequest, db : Session = Depends(start_db_session)):
    # get the active provider
    # active_provider = select_provider(db) # get active provider
    # if not active_provider: # All exhausted
        
        # salary = extract_salary(request.company_name,request.job_title)
    
    # now check for each level of API provider
    def getSalaryData():
        nonlocal db
        nonlocal request
        # get list of providers
        active_providers = active_provider_list(db)
        # if no active provider
        if not active_providers:
            raise HTTPException(status_code=429, detail='All the APIs have reached their maximum limit.')
        for provider in active_providers:
            if(provider.provider == 'jsearch'):
                salary = jsearch(request.company_name, request.job_title,request.location)
            elif(provider.provider == 'glassdoor'):
                salary = glassDoor(request.company_name, request.job_title,request.location)
            elif(provider.provider == 'jobsalarydata'):
                salary = job_salary_data_api(request.company_name, request.job_title, request.location)
            elif(provider.provider == 'careerjet'):
                salary = carrer_jet_api(request.company_name, request.job_title, request.location)

            # Analyze API response
            if 'error' not in salary:
                provider.used_calls+=1
                db.commit()
                return salary
        return salary

    salary = getSalaryData()
    ticker = extract_ticker(request.company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    about = extract_about(request.company_name)
    locations = gmapv2(request.company_name, request.location)
    stock = extract_stock_data(t_object)    
    news = extract_news(request.company_name)
    return {
        "ticker": ticker,
        "about": about,
        "offices": locations,
        "salary": 'Currently Unavailable',
        "stock_summary": stock.tail(5).to_dict(),
        "news": news,
    }