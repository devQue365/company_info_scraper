from fastapi import FastAPI
from app.schemas import InfoRequest
from app.scraper import *
from app.utils import clean_text
from yfinance import Ticker
import matplotlib.pyplot as plt
app = FastAPI()
@app.post('/company-info')
def company_info(request : InfoRequest):
    ticker = extract_ticker(request.company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    about = extract_about(request.company_name),
    salary = extract_salary(request.company_name,request.job_title)
    stock = extract_stock_data(t_object)    
    news = extract_news(request.company_name)
    return {
        "ticker": ticker,
        "about": about,
        "salary": salary,
        "stock_summary": stock.tail(5).to_dict(),
        "news": news
    }