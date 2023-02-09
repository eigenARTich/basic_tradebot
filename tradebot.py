from binance import Client            # pip install python-binance
import pandas as pd                   # pip install pandas

client = Client('BINANCE API KEY',
                'BINANCE SECRET KEY') # get your KEYS in your Binance ACC in Settings

client.get_account()

pd.DataFrame(client.get_historical_klines('BTCUSDT', '1m', '30 min ago UTC'))


# get account information displayed:
#################################################
# status = client.get_system_status()
# info = client.get_exchange_info()
# info = client.get_symbol_info('BTCUSDT')
# info = client.get_account_snapshot(type='SPOT')
# print(status)
# print(info)
#################################################

def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + '1m', '30 min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


# buy if asset fell by more when than 0.2% within the last 30 min.

def strategytest(symbol, qty, df, entry=False):
    if not entry:
        if df.Open.pct_change()[-1] < -0.002:
            order = client.create_order(symbol=symbol,
                                        side='BUY', type='Market',
                                        quantity=qty)
            print(order)
            entry = True
        else:
            print('No Trade has been executed')

# sell if asset rises by more than 0.15% or falls further by 0.15%.

    if entry:
        while True:
            sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit='ms')]
            if len(sincebuy) > 0:
                sincebuyret = (sincebuy.Open.pct_change() + 1).cumprod() - 1
                if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < -0.0015:
                    order = client.create_order(symbol=symbol,
                                                side='SELL', type='Market',
                                                quantity=qty)
                    print(order)
                    break


df = getminutedata('BTCUSDT', '1m', '30')
strategytest('BTCUSDT', 0.001, df)        # 0.001 is an example value. You have to evaluate it each time!
