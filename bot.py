import os
import time
import datetime
import pandas as pd
import ccxt
import requests
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator
from dotenv import load_dotenv

load_dotenv()

SYMBOL = 'SOL/USDT'
TIMEFRAME = '15m'
STOP_LOSS_PERCENT = -1
TRAIL_START_PROFIT = 2
TRAIL_GAP_PERCENT = 1
CAPITAL = 20

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

exchange = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_API_KEY'),
    'secret': os.getenv('BYBIT_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

trade_log = []
position = None
entry_price = None
max_price = None
position_amount = None  # Храним количество купленных монет

def fetch_ohlcv(symbol, timeframe, limit=100):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def get_usdt_balance():
    balance = exchange.fetch_balance()
    return balance['total']['USDT']

def analyze(df):
    macd = MACD(close=df['close']).macd_diff()
    obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    df['macd_diff'] = macd
    df['obv'] = obv
    df['obv_diff'] = df['obv'].diff()

    latest = df.iloc[-1]
    signal_buy = latest['macd_diff'] > 0 and latest['obv_diff'] > 0
    signal_sell = latest['macd_diff'] < 0
    return signal_buy, signal_sell

def place_order(side, amount, price=None):
    if price:
        return exchange.create_limit_order(SYMBOL, side, amount, price)
    else:
        return exchange.create_market_order(SYMBOL, side, amount)

def log_trade(action, amount, price):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    trade_log.append({'time': timestamp, 'action': action, 'amount': float(amount), 'price': float(price)})
    send_telegram(f"{action.upper()} {amount:.3f} SOL по цене {price:.3f} USDT\n⏱️ {timestamp}")

def calculate_profit():
    df = pd.DataFrame(trade_log)
    if df.empty or 'price' not in df or 'amount' not in df:
        return 0, 0
    df['total'] = df['price'] * df['amount']
    buy_sum = df[df['action'] == 'buy']['total'].sum()
    sell_sum = df[df['action'] == 'sell']['total'].sum()
    usdt_profit = sell_sum - buy_sum
    percent_profit = (usdt_profit / CAPITAL) * 100
    return usdt_profit, percent_profit

def trade():
    global position, entry_price, max_price, position_amount
    df = fetch_ohlcv(SYMBOL, TIMEFRAME)
    signal_buy, signal_sell = analyze(df)
    current_price = df.iloc[-1]['close']

    if position is None and signal_buy:
        amount = CAPITAL / current_price
        place_order('buy', amount)
        entry_price = current_price
        max_price = current_price
        position = 'long'
        position_amount = amount
        log_trade('buy', amount, entry_price)

    elif position:
        max_price = max(max_price, current_price)
        stop_loss_price = entry_price * (1 + STOP_LOSS_PERCENT / 100)
        trailing_stop_price = max_price * (1 - TRAIL_GAP_PERCENT / 100)
        amount = position_amount

        if current_price <= stop_loss_price:
            place_order('sell', amount)
            position = None
            position_amount = None
            log_trade('sell', amount, current_price)
        elif current_price >= entry_price * (1 + TRAIL_START_PROFIT / 100) and current_price <= trailing_stop_price:
            place_order('sell', amount)
            position = None
            position_amount = None
            log_trade('sell', amount, current_price)
        elif signal_sell:
            place_order('sell', amount)
            position = None
            position_amount = None
            log_trade('sell', amount, current_price)

if __name__ == '__main__':
    try:
        balance = get_usdt_balance()
        print(f"Баланс: {balance:.2f} USDT")
        send_telegram(f"Бот запущен. Баланс: {balance:.2f} USDT")
    except Exception as e:
        print("Ошибка получения баланса:", e)

    while True:
        try:
            trade()
            usdt_profit, percent_profit = calculate_profit()
            msg = f"📊 Прибыль за сессию: {usdt_profit:.2f} USDT ({percent_profit:.2f}%)"
            print(msg)
            send_telegram(msg)
            time.sleep(300)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(60)
