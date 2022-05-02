from tempfile import TemporaryFile
import cbpro
import time
from numpy import double
import cbpro

data = open('passphrase', 'r').read().splitlines()
public = data[0]
passphrase = data[1]
secret = data[2]
authClient = cbpro.AuthenticatedClient(public, secret, passphrase)
dogeAccountInfo = authClient.get_account('334285d3-d4fb-4de1-aa39-e7fd0c3078b6')
getBalance = lambda: double(dogeAccountInfo['balance'])
price = lambda: float(authClient.get_product_ticker(product_id="DOGE-USD")['price'])

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
BUY_AT_PERCENTAGE = .98
SELL_AT_PERCENTAGE = 1.02
newPriceEvery = HOUR

def buyActionHighTrades(BUY_AMOUNT):
    buyAction = lambda: authClient.place_market_order(size=BUY_AMOUNT, side="buy", product_id="DOGE-USD")
    try:                                                      # high amount of trades
        if buyAction()['message'] == 'Insufficient funds':
            return False
    except Exception:
        print(buyAction())
        print(f"New balance: {getBalance()}")
        return True

def buyActionLowTrades(BUY_AMOUNT):
    buyAction = lambda: authClient.place_market_order(size=BUY_AMOUNT, side="buy", product_id="DOGE-USD")
    try:
        if buyAction()['message'] == 'Insufficient funds':
            return False
    except Exception:
        print(buyAction())
        print(f"New balance: {getBalance()}")
        return True

def sellActionHighTrades(SELL_AMOUNT):
    sellAction = lambda: authClient.place_market_order(size=SELL_AMOUNT, side="sell", product_id="DOGE-USD")
    try:                                                      # high amount of trades
        if sellAction()['message'] == 'Insufficient funds':
            return False
    except Exception:
        print(sellAction())
        print(f"New balance: {getBalance()}")
        return True

while True:
    stallCounter = 0
    timeCounter = 0
    SELL_PRICE = price() * SELL_AT_PERCENTAGE
    BUY_PRICE = price() * BUY_AT_PERCENTAGE
    print("Current price: " + authClient.get_product_ticker(product_id="DOGE-USD")['price'])
    print(f"New buy price: {BUY_PRICE}, new sell price: {SELL_PRICE}")
    # this code refreshes every ___ seconds, refreshing data after time is reached
    while True:
        if price() <= BUY_PRICE:
            print(f"Buying DOGE! Price fell to {price()} ...")
            # stall the counter if the threshold is crossed
            # timeCounter -= REFRESH_EVERY - (REFRESH_EVERY / 4)
            # stallCounter += REFRESH_EVERY - (REFRESH_EVERY / 4)
            if buyActionLowTrades(getBalance() / 2) == True:
                # refresh buy price to account for resistance
                BUY_PRICE = price() * .996
                timeCounter -= newPriceEvery / 4
                stallCounter += newPriceEvery / 4
                
            else:
                print("Insufficient funds...")
                break


        elif price() >= SELL_PRICE:
            print(f"Selling DOGE! Price rose to {price()} ...")
            # stall the counter if the threshold is crossed
            
            if sellActionHighTrades(getBalance() / 2) == True:
                # refresh sell price to account for resistance
                SELL_PRICE = price() * 1.004
                timeCounter -= newPriceEvery / 4
                stallCounter += newPriceEvery / 4

            else:
                print("Insufficient funds...")
                break


        # refresh
        time.sleep(REFRESH_EVERY)
        timeCounter += REFRESH_EVERY
        if (timeCounter > newPriceEvery):
            print(f"{(newPriceEvery + stallCounter) / 60} minutes has passed... Stalled time: {stallCounter / 60} minutes")
            break