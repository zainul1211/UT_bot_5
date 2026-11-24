import os
import time
import requests
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IST = timezone(timedelta(hours=5, minutes=30))

STOCKS = {
    "HDFC Bank": "HDFCBANK.NS",
    "ITC": "ITC.NS",
    "Bandhan Bank": "BANDHANBNK.NS",
    "NTPC": "NTPC.NS",
    "Wipro": "WIPRO.NS"
}

def get_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
        meta = r["chart"]["result"][0]["meta"]
        return meta["regularMarketPrice"]
    except:
        return "N/A"

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

send_msg("✅ *UT Bot ON* - Sirf 5 Stocks ka Price aayega")

while True:
    try:
        msg = f"📊 *Stock Price - {datetime.now(IST).strftime('%d %b, %I:%M %p')}*\n\n"
        for name, sym in STOCKS.items():
            price = get_price(sym)
            msg += f"• *{name}*: ₹{price}\n"
        send_msg(msg)
        print("Price bhej diya")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(900)
