from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
# For plots
import io # for saving the plot to Bytes IO stream
import base64 # for encoding to base64
# for plot
import matplotlib.pyplot as plt
# from app.schemas import InfoRequest
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
            'endpoint_1': '{{base}}/status',
            'endpoint_2': '{{base}}/get-active-providers',
            'endpoint_3': '{{base}}/docs'
        }
    }


# Endpoint to get status code
@app.get('/status')
def get_status():
    url = "http://127.0.0.1:8000/"
    try:
        response = requests.get(url)
        return {"status_code": response.status_code}
    except Exception as e:
        return {
            "status_code": response.status_code,
            "error": str(e)
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


# endpoint to get employee sentiments
@app.get('/reviews')
def get_reviews(company_name: str, job_title: str):
    # ------- Status code -------
    status = get_status()
    # -------- Reviews section -------
    reviews = extract_reviews(company_name, job_title)
    return {
        'status': status,
        'company_name': company_name,
        'job_title': job_title,
        'reviews': reviews
    }


# endpoint to get company stock information
@app.get('/stocks')
def get_stocks(company_name: str, historical_insights = False, _plot = False):
    # helper function to convert the received data to json serializable form (pd data-frame -> json serializable list of dicts)
    def json_serailizable_list_of_dicts(df: pd.DataFrame) -> list:
        ''' To convert the pandas dataframe to json serializable list of dicts '''
        # check if the data frame is empty
        if(df.empty):
            return []
        # Since, many yfinance DataFrames use DatetimeIndex (i.e. dates as row indices), which can't be serialized easily.reset_index() moves the index into a regular column (usually called 'Date'), making it JSON-friendly.
        df.reset_index()
        # Now, we will force every column to be converted into generic python object
        df = df.astype(object)
        for col in df.columns:
            # check column datatype if it is 'datetime'
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                ## convert to string
                df[col] = df[col].astype(str)
            elif pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else None)
        return df.to_dict(orient = "records")
    
    ticker = extract_ticker(company_name)

    # ------- Stocks section -------
    t_object = Ticker(ticker)

    # get the latest stock insights
    latest_insights = extract_stock_data(t_object)  # we get a data frame
    ## get the latest close price if available
    if(not latest_insights.empty and "Close" in latest_insights):
        latest_closing = float(latest_insights["Close"].iloc[-1]) # numpy64 -> float
    else:
        latest_closing = None

    # get the weekly insights
    weekly_insights = extract_stock_data(t_object, period='5d')

    # get monthly stock insights
    monthly_insights = json_serailizable_list_of_dicts(extract_stock_data(t_object, period = '1mo'))

    # get annual stock insights
    annual_inights = json_serailizable_list_of_dicts(extract_stock_data(t_object, period = '1y'))
    
    # get historical stock insights
    historical_data = json_serailizable_list_of_dicts(extract_stock_data(t_object, period = 'max'))

    # for plots
    ## weekly plots
    weekly_insights['Close'].plot(title = "Stock price variation (last year)")
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    if(_plot):
        # convert plot to Base64-encoded image in JSON
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        # converting the plot to Base64 encoded image
        plot_64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    else: plot_64 = "(not specified by user)"
    
    return JSONResponse(content = {
        'company': company_name,
        'ticker': ticker,
        'stocks': {
            'latest_close_price': latest_closing,
            'latest_insights': json_serailizable_list_of_dicts(latest_insights)[0],
            'weekly_insights': json_serailizable_list_of_dicts(weekly_insights),
            'annual_insights': annual_inights,
            'historical_insights': historical_data if historical_insights else "(not specified by user)",
        },
        'plot': plot_64
    })
 









# endpoint to get company information
@app.get('/company-info')
# request : InfoRequest
def company_info(company_name: str, job_title: str, location: str, db : Session = Depends(start_db_session)):
    # get the active provider
    active_providers = get_providers(db) # get active providers
    # ------- Status code -------
    status = get_status()
    # ------- Ticker and About section -------
    ticker = extract_ticker(company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    about = extract_about(company_name)
    
    # ------- Stocks section -------
    stock = extract_stock_data(t_object)    
   
    # ------- News section -------
    news = extract_news(company_name)

    # ------- Tweets section -------
    provider = next((p for p in active_providers if p.token_id == 'twt'), None)
    if provider:
        fmap_ref = globals()[provider.name]
        # tweets = fmap_ref(company_name)
        tweets = "fetching tweets ..." # dummy statement
        if 'error' not in tweets:
            provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')
    
    # ------- Location section -------
    provider = next((p for p in active_providers if p.token_id == 'map'), None)
    if provider:
        fmap_ref = globals()[provider.name]
        # locations = fmap_ref(company_name, location)
        locations = "fetching locations ..." # dummy statement
        # look for errors
        if 'error' not in locations:
            provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')    

    # ------- Salary section -------
    provider = next((p for p in active_providers if p.token_id == 'sal'), None)
    if provider:
        fmap_ref = globals()[provider.provider]
        # salary = fmap_ref(company_name, job_title, location, db) 
        salary = "fetching salary ..."
        # look for errors
        if 'error' not in salary:
            provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')
    
    # ------- overview section -------
    if(overview_list):
        company_overview = overview_list
    else:
        provider = next((p for p in active_providers if p.token_id == 'ovr'), None)
        if provider:
            # company_overview = ov__1(company_name)
            company_overview = "fetching overview ..." # dummy statement
            # check for errors
            if('error' not in company_overview):
                provider.used_calls += 1
        else:
            raise HTTPException(status_code=429, detail='Too many requests ...')
   
    # ------ Update the database -------
    db.commit()
    return {
        "status": status.get('status_code'),
        "ticker": ticker,
        "about": about,
        'company_overview': company_overview, # (costly)
        "locations": locations,
        "salary": salary,
        "stock_summary": stock.tail(5).to_dict(),
        'latest_ceo_handles': tweets,
        "news": news,
    }