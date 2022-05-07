from tempfile import TemporaryFile
import cbpro
import time
import numpy
from datetime import datetime
# import matplotlib
# import pandas as pd

data = open('passphrase', 'r').read().splitlines()
public = data[0]
passphrase = data[1]
secret = data[2]
ws = "wss://ws-feed.prime.coinbase.com"
authClient = cbpro.AuthenticatedClient(public, secret, passphrase)
dogeAccountInfo = lambda: authClient.get_account('334285d3-d4fb-4de1-aa39-e7fd0c3078b6')
usdAccountInfo = lambda: authClient.get_account('6be3e2de-0430-47e5-bb6f-9a8361869f71')
shibAccountInfo = lambda: authClient.get_account('7617a6ac-174a-407a-9951-08beb49b8ba4')
getDogeBalance = lambda: float(dogeAccountInfo()['balance'])
getUSDBalance = lambda: float(usdAccountInfo()['balance'])
getShibBalance = lambda: float(shibAccountInfo()['balance'])

# try to trade every __ seconds
REFRESH_EVERY = 20

# how many minutes to refresh buy/sell thresholds
TEN_MIN = 600
FIFTEEN_MIN = 900
TWENTY_MIN = 1200
TWENTY_FIVE_MIN = 1500
THIRTY_MIN = 1800
HOUR = 3600

# amount constants (DOGE-USD) for how much coin to buy/sell
USD_BALANCE = lambda: getUSDBalance()
CRYPTO_BALANCE = lambda: getShibBalance()
MINIMUM = 3.8
price = float(authClient.get_product_ticker(product_id="SHIB-USD")['price'])
# print(f"Doge balance: {getDogeBalance()} DOGE")

getTotal = lambda: round((CRYPTO_BALANCE() * price), 2) + USD_BALANCE()

initialTotal = getTotal()
getNet = lambda: getTotal() - initialTotal
getNetPercent = lambda: (getNet() / initialTotal) * 100

# TRADE CONFIGS, ADJUST THESE TO YOUR LIKING
PERCENT = 1.4
ADJUST_PERCENT = 1
toPercent = PERCENT / 100
BUY_AT_PERCENTAGE = 1 - toPercent
SELL_AT_PERCENTAGE = 1 + toPercent
newPriceEvery = HOUR

buyPercent = lambda: round(((1 - BUY_AT_PERCENTAGE) * 100), 4)
sellPercent = lambda: round(((SELL_AT_PERCENTAGE - 1) * 100), 4)

def buyActionLowTrades(BUY_AMOUNT):
    buySize = round(BUY_AMOUNT, 0)                                                             # ROUND TO 1 FOR DOGE, 0 FOR SHIB
    print(authClient.place_market_order(size=buySize, side="buy", product_id="SHIB-USD"))

def sellActionLowTrades(SELL_AMOUNT):
    sellSize = round(SELL_AMOUNT, 0)
    print(authClient.place_market_order(size=sellSize, side="sell", product_id="SHIB-USD"))

while True:
    print(f"Time started: {datetime.now()}")
    print(f"BALANCES:\nUSD: {USD_BALANCE()}\nSHIB: {CRYPTO_BALANCE()}")
    print(f"Total portfolio: {initialTotal}")
    print(f"BUY CONFIG: {buyPercent()}%   SELL CONFIG: {sellPercent()}%")
    stallCounter = 0
    timeCounter = 0
    extraStallCounter = 0
    totalActions = 0
    # price = float(authClient.get_product_ticker(product_id="DOGE-USD")['price'])
    price = float(authClient.get_product_ticker(product_id="SHIB-USD")['price'])
    # SELL_PRICE = round((price * SELL_AT_PERCENTAGE), 4)
    # BUY_PRICE = round((price * BUY_AT_PERCENTAGE), 4)
    SELL_PRICE = price * SELL_AT_PERCENTAGE
    # BUY_PRICE = price * BUY_AT_PERCENTAGE
    BUY_PRICE = price * BUY_AT_PERCENTAGE
    print(f"Current price: {price}")
    print(f"New buy price: {BUY_PRICE}, new sell price: {SELL_PRICE}")
    # this code refreshes every ___ seconds, refreshing data after time is reached
    while True:
        # price = float(authClient.get_product_ticker(product_id="DOGE-USD")['price'])
        price = float(authClient.get_product_ticker(product_id="SHIB-USD")['price'])
        if price <= BUY_PRICE:
            print(f"Buying SHIB! Price fell to {price} ...")
            buyActionLowTrades(((USD_BALANCE() / price)) / 2)                   # half of USD balance in DOGE
            # refresh buy/sell price to account for resistance
            # if totalActions == 0:
            SELL_PRICE = price * 1.01
            BUY_PRICE = price * .99
            extraStallCounter = 0
            totalActions += 1
            # CRYPTO_BALANCE += (USD_BALANCE / 2) / price
            # USD_BALANCE = USD_BALANCE / 2
            # print(f"BALANCES:\nUSD: {USD_BALANCE()}\nSHIB: {CRYPTO_BALANCE()}")

        elif price >= SELL_PRICE:
            print(f"Selling SHIB! Price rose to {price} ...")
            sellActionLowTrades(CRYPTO_BALANCE() / 2)
            # refresh buy/sell price to account for resistance
            # if totalActions == 0:
            BUY_PRICE = price * .99
            SELL_PRICE = price * 1.01
            extraStallCounter = 0
            totalActions += 1
            # USD_BALANCE += (CRYPTO_BALANCE / 2) * price
            # CRYPTO_BALANCE = CRYPTO_BALANCE / 2
            # print(f"BALANCES:\nUSD: {USD_BALANCE()}\nSHIB: {CRYPTO_BALANCE()}")


        # refresh
        time.sleep(REFRESH_EVERY)
        timeCounter += REFRESH_EVERY

        if ((price - BUY_PRICE) / price) * 100 <= .10 and extraStallCounter < 3:
            timeCounter -= newPriceEvery / 12                           # give extra 5 min if 10% away from buy price
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 10% away from BUY price... {datetime.now()}")

        elif ((price - BUY_PRICE) / price) * 100 <= .15 and extraStallCounter < 1:            # give extra 10 min if 15% away from buy price
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 15% away from BUY price... {datetime.now()}")

        elif ((SELL_PRICE - price) / price) * 100 <= .10 and extraStallCounter < 3:
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 10% away from SELL price... {datetime.now()}")

        elif ((SELL_PRICE - price) / price) * 100 <= .15 and extraStallCounter < 1:
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 15% away from SELL price... {datetime.now()}")
            
        if timeCounter == newPriceEvery / 2:
            print(f"{(timeCounter + stallCounter) / 60} minutes has passed, continuing...")
        if (timeCounter > newPriceEvery):
            print(f"{(newPriceEvery + stallCounter) / 60} minutes has passed, HOUR COMPLETE... Stalled time: {stallCounter / 60} minutes\n")
            print(f"Net: {getNet()}, {getNetPercent()}%")
            print()
            break