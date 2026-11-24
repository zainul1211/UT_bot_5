import os, requests, time
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IST = timezone(timedelta(hours=5, minutes=30))

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def get_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=5m&range=1d"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
    res = r["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    closes = [c for c in q["close"] if c is not None]
    highs = [c for c in q["high"] if c is not None]
    lows = [c for c in q["low"] if c is not None]
    vols = [c if c else 0 for c in q["volume"]]
    return closes, highs, lows, vols

def calc_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    if avg_loss == 0: return 100
    rs = avg_gain/avg_loss
    return 100 - (100/(1+rs))

def calc_ema(data, period):
    k = 2/(period+1)
    ema = data[0]
    for p in data[1:]:
        ema = p*k + ema*(1-k)
    return ema

send_msg("✅ *NIFTY SIGNAL BOT ON* - VWAP + EMA + RSI")

last_signal = ""
while True:
    try:
        closes, highs, lows, vols = get_data()
        price = closes[-1]
        typical = [(highs[i]+lows[i]+closes[i])/3 for i in range(len(closes))]
        vwap = sum(t*v for t,v in zip(typical, vols))/sum(vols) if sum(vols)>0 else price
        ema9 = calc_ema(closes, 9)
        ema21 = calc_ema(closes, 21)
        rsi = calc_rsi(closes)
        strike = round(price/50)*50
        signal = "WAIT"
        if price > vwap and ema9 > ema21 and rsi > 50 and rsi < 70:
            signal = "BUY_CE"
        elif price < vwap and ema9 < ema21 and rsi < 50 and rsi > 30:
            signal = "BUY_PE"
        t = datetime.now(IST).strftime('%I:%M %p')
        if signal != last_signal and signal != "WAIT":
            if signal == "BUY_CE":
                send_msg(f"🟢 *STRONG BUY NIFTY CE*\n\nPrice: {price:.2f}\nStrike: *{strike} CE*\nVWAP: {vwap:.2f} (Price Upar Hai)\nEMA 9: {ema9:.2f} > EMA 21: {ema21:.2f}\nRSI: {rsi:.1f}\nTime: {t}\n\n⚠️ Paper Trade se pehle check karo, ye SEBI advice nahi hai.")
            else:
                send_msg(f"🔴 *STRONG BUY NIFTY PE*\n\nPrice: {price:.2f}\nStrike: *{strike} PE*\nVWAP: {vwap:.2f} (Price Neeche Hai)\nEMA 9: {ema9:.2f} < EMA 21: {ema21:.2f}\nRSI: {rsi:.1f}\nTime: {t}\n\n⚠️ Paper Trade se pehle check karo, ye SEBI advice nahi hai.")
            last_signal = signal
        elif signal == "WAIT":
            last_signal = "WAIT"
        print(f"{t} Price:{price:.2f} VWAP:{vwap:.2f} RSI:{rsi:.1f} Signal:{signal}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(300)
