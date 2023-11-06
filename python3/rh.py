#!bin/python
import robin_stocks.robinhood as r
import csv
import collections
import os
from datetime import datetime
from dotenv import load_dotenv


class csvParser:

    def __init__(self, csvFileName):
        self.csvFileName = csvFileName

    def updateProfile(self):
        pass


class Tranche:

    def __init__(self, tranche):
        self.shares = tranche["shares"]
        self.dateAcquired = tranche["dateAcquired"]
        self.avgPrice = tranche["avgPrice"]


class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.tranches = []

    def createTranche(self, tranche):
        """Adds a tranche object to the running list of tranche objects."""
        self.tranches.append(Tranche(tranche))

    def getLongTermCapitalGainsTranche(self):
        """
        Prints out all stock tranches tranches
        that are older the 365 days (one year).
        """
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

    def getAllTranches(self):
        """
        Prints out all tranches in this stock.
        """
        for tranche in self.tranches:
            print(f"\n\tShares: {tranche.shares}\n\t",
                  f"Date Acquired: {tranche.dateAcquired}\n\t",
                  f"Avg Price: {tranche.avgPrice}",
                  sep="",
                  end="\n")


class Portfolio:

    def __init__(self):
        self.positions = {}

    def createStock(self, symbol: str) -> None:
        """
        Creates a stock when given a symbol to identify it by
        """
        self.positions[symbol] = Stock(symbol)

    def getStock(self, symbol: str) -> Stock:
        """
        Get a stock object given a valid symbol
        """
        return self.positions[symbol]


if __name__ == "__main__":
    load_dotenv()
    user = os.getenv('username')
    password = os.getenv('password')
    mfaCode = input("enter the MFA code")
    login = r.login(user, password, mfa_code=mfaCode)
    profile = collections.defaultdict(list)
    IGNORELIST = ['GRPN', 'FIT', 'ATVI']
    r.export_completed_stock_orders(".", "test.csv")
    with open('test.csv', 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in reversed(list(csvreader)):
            symbol = row["symbol"]
            if symbol in IGNORELIST:
                continue
            side = row['side']
            tranche = {"shares": int(float(row['quantity'])),
                       "dateAcquired": row['date'],
                       "avgPrice": float(row['average_price'])}
            match side:
                case 'buy':
                    profile[symbol].append(tranche)
                case 'sell':
                    while tranche["shares"] > 0:
                        profile[symbol][-1]["shares"] -= 1
                        tranche["shares"] -= 1
                        if profile[symbol][-1]["shares"] == 0:
                            profile[symbol].pop()

    portfolio = Portfolio()

    for symbol, tranches in profile.items():
        if not tranches:
            continue
        portfolio.createStock(symbol)
        stock = portfolio.getStock(symbol)
        for tranche in tranches:
            stock.createTranche(tranche)

    for symbol, stockObj in portfolio.positions.items():
        print(f'\nSymbol: {symbol}')
        stockObj.getAllTranches()
