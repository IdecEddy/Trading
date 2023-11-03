#!bin/python
import robin_stocks.robinhood as r
import csv
import collections
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
user = os.getenv('username')
password = os.getenv('password')
login = r.login(user, password)
profile = collections.defaultdict(list)
IGNORELIST = ['GRPN', 'FIT']


class Tranche:

    def __init__(self, tranche):
        self.shares = tranche[0]
        self.dateAcquired = tranche[1]
        self.avgPrice = tranche[2]


class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.tranches = []

    def createTranche(self, tranche):
        self.tranches.append(Tranche(tranche))

    def getLongTermCapitalGainsTranche(self):
        for tranche in self.tranches:
            if "." in tranche.dateAcquired:
                dateFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
            else:
                dateFormat = "%Y-%m-%dT%H:%M:%SZ"
            dateObject = datetime.strptime(tranche.dateAcquired, dateFormat)
            currentDate = datetime.now()
            timeDifference = currentDate - dateObject
            oneYear = 365
            if timeDifference.days >= oneYear:
                print(f"\n\tShares: {tranche.shares}\n\t",
                      f"Date Acquired: {tranche.dateAcquired}\n\t",
                      f"Avg Price: {tranche.avgPrice}",
                      sep="",
                      end="\n")
        print("")

class Portfolio:

    def __init__(self):
        self.positions = {}

    def createStock(self, symbol: str) -> None:
        self.positions[symbol] = Stock(symbol)

    def getStock(self, symbol: str) -> Stock:
        return self.positions[symbol]


if __name__ == "__main__":
    with open('test.csv', 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in reversed(list(csvreader)):
            symbol = row["symbol"]
            if symbol in IGNORELIST:
                continue
            side = row['side']
            tranche = [int(float(row['quantity'])),
                       row['date'],
                       float(row['average_price'])]
            match side:
                case 'buy':
                    profile[symbol].append(tranche)
                case 'sell':
                    while tranche[0] > 0:
                        profile[symbol][-1][0] -= 1
                        tranche[0] -= 1
                        if profile[symbol][-1][0] == 0:
                            profile[symbol].pop()

    portfolio = Portfolio()

    for symbol, tranches in profile.items():
        if not tranches:
            continue
        portfolio.createStock(symbol)
        stock = portfolio.getStock(symbol)
        for tranche in tranches:
            stock.createTranche(tranche)
    print(portfolio.positions['AMD'].tranches)
    print(f'\nSymbol: {portfolio.positions["MMM"].symbol}')
    portfolio.positions['MMM'].getShortTermCapitalGainsTranche()

# r.export_completed_stock_orders(".", "test.csv")
