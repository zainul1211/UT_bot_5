import os, requests, time
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IST = timezone(timedelta(hours=5, minutes=30))

STOCKS = {
    "HDFC Bank": "HDFCBANK.NS",
    "Wipro": "WIPRO.NS",
    "Bandhan Bank": "BANDHANBNK.NS",
    "ITC": "ITC.NS",
    "NTPC": "NTPC.NS"
}

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=5d"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
    res = r["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    closes = [c for c in q["close"] if c is not None]
    highs = [c for c in q["high"] if c is not None]
    lows = [c for c in q["low"] if c is not None]
    return closes, highs, lows

def calc_ut(closes, highs, lows):
    ATR_PERIOD = 10
    ATR_MULT = 1.0
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    atr = sum(trs[-ATR_PERIOD:]) / ATR_PERIOD
    price = closes[-1]
    prev_close = closes[-2]
    upper = prev_close + (ATR_MULT * atr)
    lower = prev_close - (ATR_MULT * atr)
    if price > upper:
        return "BUY", price
    elif price < lower:
        return "SELL", price
    else:
        return "WAIT", price

def is_market_open():
    now = datetime.now(IST)
    # Saturday = 5, Sunday = 6 - Market band
    if now.weekday() >= 5:
        return False
    # Market time 9:15 AM se 3:30 PM tak
    start = now.replace(hour=9, minute=15, second=0)
    end = now.replace(hour=15, minute=30, second=0)
    return start <= now <= end

send_msg("✅ *UT BOT ON - 5 Stocks*\nBot chalu rahega, signal sirf 9:15 - 3:30 me aayega")

last = {name: None for name in STOCKS}

while True:
    try:
        now = datetime.now(IST)
        t = now.strftime('%I:%M %p')

        # Market band hai to signal mat bhejo, bas wait karo
        if not is_market_open():
            print(f"{t} Market BAND hai, wait kar raha hu...", flush=True)
            time.sleep(60)
            continue

        for name, sym in STOCKS.items():
            closes, highs, lows = get_data(sym)
            signal, price = calc_ut(closes, highs, lows)
            print(f"{t} {name}: {price:.2f} Signal:{signal}", flush=True)

            # Pehli baar chalu hone pe purana signal mat bhejo
            if last[name] is None:
                last[name] = signal
                continue

            if signal != last[name] and signal != "WAIT":
                if signal == "BUY":
                    send_msg(f"🟢 *UT BOT - BUY {name}*\n\nPrice: ₹{price:.2f}\nTime: {t}\n\nChart me UT BUY aaya hai.")
                else:
                    send_msg(f"🔴 *UT BOT - SELL {name}*\n\nPrice: ₹{price:.2f}\nTime: {t}\n\nChart me UT SELL aaya hai.")
                last[name] = signal
            if signal == "WAIT":
                last[name] = "WAIT"
            time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(60)
