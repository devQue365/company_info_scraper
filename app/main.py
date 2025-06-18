from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
# For plots
import matplotlib.pyplot as plt
from matplotlib_inline.backend_inline import set_matplotlib_formats
import io # for saving the plot to Bytes IO stream
import base64 # for encoding to base64
from dateutil.relativedelta import relativedelta # (it can also take leap-years into consideration)
# from app.schemas import InfoRequest
from app.scraper import *
from app.utils import clean_text
from yfinance import Ticker
import matplotlib.pyplot as plt
# salary module
from app.Salary.salary_estimates import *
# location module
from app.location import *
# tweets module
from app.tweets import *
# overview module
from app.overview import *
# database module
from app.database.database import init_db, sessionLocal, start_db_session
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.models import CACHE_SAL, CACHE_OVR, CACHE_MAP, TWT
from app.leaf import tweet_init_leaf, map_init_leaf, salary_init_leaf, overview_init_leaf
# API usage scheme
from app.database.api_usage_scheme import get_providers
# NLP processing
from app.database.insert import generic_cache_insert, generic_insert, generic_delete
from app.Salary.insert import salary_cache_insert
from app.Essentials.semantic_similarity import semantic_match
from app.Essentials.features import assistant_call


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
def root():
    return {
        'message': 'Welcome to the Company_Info_Scraper V-1.0 API!',
        'explore': JSONResponse(
            content = {
                'endpoint_1': '{{base}}/status',
                'endpoint_2': '{{base}}/get-active-providers',
                'endpoint_3': '{{base}}/reviews',
                'endpoint_4': '{{base}}/stocks',
                'endpoint_5': '{{base}}/news',
                'endpoint_6': '{{base}}/overview',
                'endpoint_7': '{{base}}/salary',
                'endpoint_8': '{{base}}/location',
                'endpoint_9': '{{base}}/twitter_handle',
                'endpoint_10': '{{base}}/financials',
                'testing_url': '{{base}}/docs' 
            }
        )
    }
    

# endpoint to get status code
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


# endpoint to get active api providers
@app.get('/get-active-providers')
def get_active_api(db : Session = Depends(start_db_session)):
    # here, we are getting a DB session by calling start_db_session() automatically [dependency injection 'Depend'].
    active_providers = get_providers(db) # get active providers list
    print(active_providers)
    if not active_providers: # All exhausted
        raise HTTPException(status_code=429, detail='All the providers have reached their maximum limit.')
    return JSONResponse(content = {
        "active_providers": active_providers
    })


# endpoint to get employee sentiments
@app.get('/reviews')
def get_reviews(company_name: str, job_title: str):
    # ------- Status code -------
    status = get_status()
    # -------- Reviews section -------
    reviews = extract_reviews(company_name, job_title)
    return JSONResponse(content = {
        'status': status,
        'company_name': company_name.capitalize(),
        'job_title': job_title.capitalize(),
        'reviews': reviews
    })


# endpoint to get company stock information
@app.get('/stocks')
def get_stocks(company_name: str, historical_insights = False, _plot: str = 'N', _download = False):
    ''' Get the company's stock information '''
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
    weekly_insights = extract_stock_data(t_object, period='1wk')

    # get monthly stock insights (interval : 5d)
    monthly_insights = extract_stock_data(t_object, period = '1mo', interval = '7d')

    # get annual stock insights (interval : 1mo)
    annual_insights = extract_stock_data(t_object, period = '1y', interval = '1mo')
    
    # get historical stock insights (interval : 1y)
    historical_data = extract_stock_data(t_object, period = 'max',interval = '1y')

    # construct plots
    def constructPlot(period):
        nonlocal ticker, weekly_insights, monthly_insights, annual_insights, historical_data
        set_matplotlib_formats('svg') # highly scalable and optimized resolution
        # get current day
        current_day = datetime.today()
        last_month_cred = format(current_day - relativedelta(months=1), "%B %Y")
        last_year = format(current_day - relativedelta(years=1), "%Y")
        mapped_titles = {
            'W': f"Weekly Movement of {ticker} Stock",
            'M': f"Monthly Momentum: How {ticker} performed in {last_month_cred} ?",
            'Y': f"Year in Charts: {ticker} Stock Price Trends in {last_year}",
            'H': f"{ticker} Through the Ages: Full Stock Price History Since IPO"
        }
        mapped_X_labels = {
            'W': "Days",
            'M': "Week",
            'Y': "Months",
            'H': "Years",
        }
        insight_to_be_used = weekly_insights if (period == 'W') else monthly_insights if (period == 'M') else annual_insights if (period == 'Y') else historical_data if (period == 'H') else None
        # main plot logic
        insight_to_be_used['Close'].plot(title = mapped_titles.get(period, f"{ticker} Stock Trends"))
        plt.xlabel(mapped_X_labels.get(period, "Standard TimeFrame"))
        plt.ylabel("Stock Price (USD)")
        plt.xticks(rotation = 45)
        plt.figure(figsize=(15,8))
        plt.tight_layout()
        plt.legend(loc = 'best')
        if(_download):
            constructPlot()
            plt.savefig(f"{ticker}_stock_data.svg", bbox_inches = 'tight')

    if(_plot):
        # convert plot to Base64-encoded image in JSON
        constructPlot(_plot)
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        # converting the plot to Base64 encoded image
        plot_64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

    else: 
        plot_64 = "(not specified by user)"

    

    return JSONResponse(content = {
        'company': company_name.capitalize(),
        'ticker': ticker,
        'stocks': {
            'latest_close_price': latest_closing,
            'latest_insights': json_serailizable_list_of_dicts(latest_insights)[0],
            'weekly_insights': json_serailizable_list_of_dicts(weekly_insights),
            'annual_insights': json_serailizable_list_of_dicts(annual_insights),
            'historical_insights': json_serailizable_list_of_dicts(historical_data) if (historical_insights) else "(not specified by user)",
        },
        'plot': plot_64
    })
 

# endpoint to get company's news
@app.get('/news')
def get_news(company_name: str, field_of_interest: str):
    '''Returns latest news influenced by company, field of interest and a mix of spicy criticisms, achievements and much more just in one go.
    Consumes "1" request / call.
    '''
    # ------- News section -------
    news = extract_news(company_name, field_of_interest)
    
    return JSONResponse(
        content = {
            'company': company_name.capitalize(),
            'field_of_interest': field_of_interest.capitalize(),
            'news_feed': news
        }
    )



# endpoint to get company's overview
@app.get('/overview')
def get_company_overview(company_name: str, db : Session = Depends(start_db_session)):
    ''' 
    Returns the company's overview based on company_name. Each call consumes "3" requests (costly)
    '''
    try:
        # get the active provider
        active_providers = get_providers(db) # get active providers      
        provider = next((p for p in active_providers if p.token_id == 'OVR'), None)
        if provider:
            company_overview = ov__1(company_name, db)
            # company_overview = "fetching overview ..." # dummy statement
            # check for errors
        else:
            raise HTTPException(status_code=429, detail='Too many requests ...')
        # make changes visible in database
        if('exception_status' not in company_overview):
                provider.used_calls += 1
        db.commit()
        return JSONResponse(content = {
            'company_name': company_name.capitalize(),
            'overview': company_overview
        })
    
    except Exception as e:
        return JSONResponse(content = {
            'error': str(e)
        })



# endpoint to get company's salary + semantic matching enabled
@app.get('/salary_estimation')
def get_salary_estimation(company_name: str, job_title: str, location: str, db: Session = Depends(start_db_session)):
    '''Returns salary estimates based on company, job role and location factors. Consumes "2" requests / call.'''
    # reset the cache to remove outdated data
    ''' search cache first and then proceed to calling api '''
    reset_table(CACHE_SAL, db, 'company_name')
    # perform a semantic match accross the cache database
    matched_record : object = semantic_match(
        db,
        CACHE_SAL,
        ['company_name', 'job_title', 'location'],
        [company_name, job_title, location]
    )
    if(matched_record):
        salary = matched_record.salary_data
        print("\033[35m\033[1mGot the salary data from database\033[0m")
        return JSONResponse(
            content = {
                'company_name': matched_record.company_name,
                'job_title': matched_record.job_title,
                'location': matched_record.location,
                'salary_data': salary
            }
        )
    # get the active provider
    active_providers = get_providers(db)
    # get the salary provider
    provider = next((p for p in active_providers if p.token_id == 'SAL'), None)
    if provider:
        # fmap_ref = globals()[provider.provider]
        # salary = fmap_ref(company_name, job_title, location) 
        salary = "fetching salary ..."
        # look for errors
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')
    
    if 'error' not in salary:
        provider.used_calls+=2

    # Add the record to cache
    type = provider.type
    confidence = provider.confidence
    salary_cache_insert(
        company_name.lower(), 
        job_title.lower(), 
        location.lower(), 
        salary, 
        type= type, 
        confidence=confidence, 
        db=db
    )
    db.commit()
    return JSONResponse(
        content = {
            'company_name': company_name,
            'job_title': job_title,
            'location': location,
            'salary_data': salary
        })



# endpoint to get company's offices + semantic matching enabled
@app.get('/location')
def get_work_locations(company_name: str, location: str, db: Session = Depends(start_db_session)):
    ''' 
    Returns company's operating locations based on region specified by user. It may take a while to load the data. But don't worry and sit upright and be ready !
    Consumes "1" request / call
    '''
    try:
        # first of all search the cache storage
        # always reset the table first
        reset_table(CACHE_MAP, db, _member = "company_name")
        # now consider fetching location data
        matched_record = semantic_match(
            db,
            CACHE_MAP, 
            ['company_name', 'location'],
            [company_name, location],
        )
        if(matched_record):
            print("\033[35m\033[1mGot the location data from database\033[0m")
            return JSONResponse(
            content = {
                'company_name': matched_record.company_name,
                'location': matched_record.location,
                'work_locations': matched_record.location_data,
            }
        )
        # get the active provider
        active_providers = get_providers(db)     
        provider = next((p for p in active_providers if p.token_id == 'MAP'), None)
        if provider:
            fmap_ref = globals()[provider.name]
            work_locations = fmap_ref(company_name, location)
            # locations = "fetching locations ..." # dummy statement
            # look for errors
            if 'error' not in work_locations:
                provider.used_calls+=1
        else:
            raise HTTPException(status_code=429, detail='Too many requests ...') 
        
        # check whether the data we got is accurate or not -> call assistant
        cleaned_work_locations = assistant_call(work_locations)
        print(cleaned_work_locations)
        # if there is a need to clean work locations
        if(cleaned_work_locations):
            work_locations = cleaned_work_locations
        # add to cache
        generic_cache_insert(
            db,
            CACHE_MAP,
            ['company_name', 'location', 'location_data'],
            [company_name, location, work_locations],
        )
        return JSONResponse(
            content = {
                'company_name': company_name,
                'location': location,
                'work_locations': work_locations
            }
        )

    except Exception as e:
        return JSONResponse(content = {
            'message': 'Exception encountered while fetching results ...',
            'exception_status': str(e)
        })

@app.get('/twitter_handle')
# endpoint to get company's tweets
def get_tweets(company_name: str, job_title: str, limit:int = 5, db: Session = Depends(start_db_session)):
    # add new twitter records
    # generic_insert(
    #     db,
    #     TWT,
    #     ['name', 'provider', 'used_calls', 'total_calls', 'reset_type', 'last_reset'],
    #     ['twt__5', 'twitter_api', 0, 100, 'M', datetime.now()],
    # )
    # get the active provider
    active_providers = get_providers(db)
    provider = next((p for p in active_providers if p.token_id == 'TWT'), None)
    if provider:
        fmap_ref = globals()[provider.name]
        tweets = fmap_ref(company_name, job_title, limit)
        # tweets = twt__5(company_name, job_title, limit)
        # tweets = "fetching tweets ..." # dummy statement
        # if 'error' not in tweets:
            # provider.used_calls+=1
    else:
        raise HTTPException(status_code=429, detail='Too many requests ...')

    return JSONResponse(
        content = {
            'company_name': company_name,
            'tweets': tweets
        }
    )










































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
    if(None):
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