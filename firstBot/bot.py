from tempfile import TemporaryFile
import cbpro
import time
import numpy
from datetime import datetime

data = open('passphrase', 'r').read().splitlines()
public = data[0]
passphrase = data[1]
secret = data[2]
authClient = cbpro.AuthenticatedClient(public, secret, passphrase)
dogeAccountInfo = authClient.get_account('334285d3-d4fb-4de1-aa39-e7fd0c3078b6')
getBalance = lambda: float(dogeAccountInfo['balance'])
price = lambda: float(authClient.get_product_ticker(product_id="DOGE-USD")['price'])
print(f"Balance: {getBalance()} DOGE")

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
MINIMUM = 3.8
getMaxAvail = lambda: getBalance()

# TRADE CONFIGS, ADJUST THESE TO YOUR LIKING
BUY_AT_PERCENTAGE = .992
SELL_AT_PERCENTAGE = 1.008
newPriceEvery = HOUR

def buyActionLowTrades(BUY_AMOUNT):
    buySize = str(round(BUY_AMOUNT, 4))
    buyAction = lambda: authClient.place_market_order(size=buySize, side="buy", product_id="DOGE-USD")
    try:
        print(buySize)
        print(buyAction())
        print(f"New balance: {getBalance()}")
        return True
    except Exception:
        return False

def sellActionLowTrades(SELL_AMOUNT):
    sellSize = str(round(SELL_AMOUNT, 4))
    sellAction = lambda: authClient.place_market_order(size=sellSize, side="sell", product_id="DOGE-USD")
    try:                                                      # high amount of trades
        print(sellSize)
        print(sellAction())
        print(f"New balance: {getBalance()}")
        return True
    except Exception:
        return False

while True:
    print(f"Time started: {datetime.now()}")
    stallCounter = 0
    timeCounter = 0
    extraStallCounter = 0
    SELL_PRICE = str(round((price() * SELL_AT_PERCENTAGE), 4))
    BUY_PRICE = str(round((price() * BUY_AT_PERCENTAGE), 4))
    print("Current price: " + authClient.get_product_ticker(product_id="DOGE-USD")['price'])
    print(f"New buy price: {BUY_PRICE}, new sell price: {SELL_PRICE}")
    # this code refreshes every ___ seconds, refreshing data after time is reached
    while True:
        if price() <= BUY_PRICE:
            print(f"Buying DOGE! Price fell to {price()} ...")
            if buyActionLowTrades(getBalance() / 2) == True:
                # refresh buy/sell price to account for resistance
                SELL_PRICE = price() * 1.003
                BUY_PRICE = price() * .997
                extraStallCounter = 0
                print(f"Stalling {(newPriceEvery / 12) / 60} minutes... ")
                
            else:
                print("Insufficient funds...")
                break


        elif price() >= SELL_PRICE:
            print(f"Selling DOGE! Price rose to {price()} ...")
            if sellActionLowTrades(getBalance() / 2) == True:
                # refresh buy/sell price to account for resistance
                SELL_PRICE = price() * 1.003
                BUY_PRICE = price() * .997
                extraStallCounter = 0
                print(f"Stalling {(newPriceEvery / 12) / 60} minutes... ")

            else:
                print("Insufficient funds...")
                break


        # refresh
        time.sleep(REFRESH_EVERY)
        timeCounter += REFRESH_EVERY
        if ((price() - BUY_PRICE) / price()) * 100 <= .10 and extraStallCounter < 2:
            timeCounter -= newPriceEvery / 12                           # give extra 5 min if 10% away from buy price
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 10% away from BUY price... {datetime.now()}")

        elif ((price() - BUY_PRICE) / price()) * 100 <= .15 and extraStallCounter < 1:            # give extra 10 min if 15% away from buy price
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 15% away from BUY price... {datetime.now()}")

        elif ((SELL_PRICE - price()) / price()) * 100 <= .10 and extraStallCounter < 2:
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 10% away from SELL price... {datetime.now()}")

        elif ((SELL_PRICE - price()) / price()) * 100 <= .15 and extraStallCounter < 1:
            timeCounter -= newPriceEvery / 12
            stallCounter += newPriceEvery / 12
            extraStallCounter += 1
            print(f"Stalling {(newPriceEvery / 12) / 60} minutes! 15% away from SELL price... {datetime.now()}")
            
        if timeCounter == newPriceEvery / 2:
            print(f"{timeCounter / 60} minutes has passed, continuing...")
        if (timeCounter > newPriceEvery):
            print(f"{(newPriceEvery + stallCounter) / 60} minutes has passed... Stalled time: {stallCounter / 60} minutes")
            break