from fastapi import FastAPI
from app.schemas import InfoRequest
from app.scraper import *
from yfinance import Ticker
app = FastAPI()
@app.post('/company-info')
def company_info(request : InfoRequest):
    ticker = extract_ticker(request.company_name)
    if(not ticker):
        return {"error" : "unidentified company"}
    t_object = Ticker(ticker)
    stock = extract_stock_data(t_object, '1d')
    news = extract_news(request.company_name)
    return {
        "ticker": ticker,
        "stock_summary": stock.tail(5).to_dict(),
        "news": news
    }