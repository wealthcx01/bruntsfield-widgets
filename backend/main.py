# main.py - Bruntsfield Widget Backend for OpenBB Workspace
from pathlib import Path
import json
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from functools import wraps
import asyncio

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Telegram notification function
def send_telegram(message: str):
    """Send notification to Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Telegram notification failed: {e}")

# Initialize widgets dictionary
WIDGETS = {}

# Decorator to register widgets
def register_widget(widget_config):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

# Initialize FastAPI
app = FastAPI(
    title="Bruntsfield Widget Backend",
    description="Financial widgets for OpenBB Workspace",
    version="0.1.0"
)

# CORS configuration - REQUIRED for OpenBB Workspace
origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:3000",
    "http://localhost:6900",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve widgets.json - REQUIRED ENDPOINT
@app.get("/widgets.json")
def get_widgets():
    return JSONResponse(content=WIDGETS)

# Serve apps.json - REQUIRED ENDPOINT
@app.get("/apps.json")
def get_apps():
    apps_path = Path(__file__).parent / "apps.json"
    if apps_path.exists():
        return JSONResponse(content=json.load(apps_path.open()))
    return JSONResponse(content={})

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "widgets": len(WIDGETS)}


# ============================================================
# WIDGETS GO BELOW THIS LINE
# ============================================================

@register_widget({
    "name": "Portfolio Allocation",
    "description": "Shows portfolio allocation by sector as a donut chart",
    "category": "Portfolio",
    "type": "chart",
    "endpoint": "portfolio_allocation",
    "gridData": {"w": 20, "h": 12},
    "source": "Bruntsfield",
    "data": {
        "dataKey": "data",
        "chart": {
            "type": "pie"
        }
    },
    "params": [
        {
            "paramName": "symbols",
            "value": "AAPL,MSFT,GOOGL,AMZN,NVDA",
            "label": "Ticker Symbols",
            "type": "text",
            "description": "Comma-separated list of tickers"
        }
    ]
})
@app.get("/portfolio_allocation")
async def portfolio_allocation(symbols: str = "AAPL,MSFT,GOOGL,AMZN,NVDA"):
    """Get portfolio allocation data grouped by sector."""
    from openbb import obb
    
    ticker_list = [s.strip() for s in symbols.split(",")]
    results = []
    
    for ticker in ticker_list:
        try:
            profile = obb.equity.profile(ticker, provider="yfinance")
            if profile.results:
                p = profile.results[0]
                results.append({
                    "symbol": ticker,
                    "name": getattr(p, 'name', ticker),
                    "sector": getattr(p, 'sector', 'Unknown') or "Unknown",
                    "weight": 1.0 / len(ticker_list),
                    "value": 10000 / len(ticker_list),
                })
        except Exception as e:
            results.append({
                "symbol": ticker,
                "name": ticker,
                "sector": "Error",
                "weight": 1.0 / len(ticker_list),
                "value": 0,
            })
    
    # Aggregate by sector
    aggregated = {}
    for r in results:
        sector = r["sector"]
        if sector not in aggregated:
            aggregated[sector] = {"label": sector, "value": 0}
        aggregated[sector]["value"] += r["weight"] * 100
    
    return {"data": list(aggregated.values())}


# Startup notification
@app.on_event("startup")
async def startup_event():
    send_telegram(f"🚀 *Bruntsfield Backend Started*\n\nWidgets loaded: {len(WIDGETS)}\nEndpoint: http://localhost:6900")
