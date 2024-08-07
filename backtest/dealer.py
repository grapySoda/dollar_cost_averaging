from .stock import Stock
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from datetime import datetime

TAX_TAIWAN = 1.003


class Transaction:
    def __init__(self, stock, date, price, quantity, cost, action, roi=0):
        self.stock = stock
        self.date = datetime.strptime(date, "%Y/%m/%d")
        self.price = price
        self.quantity = quantity
        self.cost = cost
        self.action = action
        self.roi = roi

    def __repr__(self):
        return f"Transaction(date={self.date.strftime('%Y/%m/%d')}, price={self.price}, quantity={self.quantity}, cost={self.cost})"


class Dealer:

    def __init__(
        self, token, start_date, end_date, commissionRatio=0.0, commissionCash=0
    ):
        self._figures = 1
        self._cash = 0
        self._stocks = {}
        self._token = token
        self._start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self._end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if commissionRatio > 1.0 or commissionRatio == 0.0:
            self._commissionRatio = commissionRatio
        else:
            self._commissionRatio = 1 + commissionRatio
        self._commissionCash = commissionCash

    def add(self, country, id):
        self._stocks[id] = Stock(country, id, self._token)
        start, end = self.getDuration(id)
        if self._start_date < start:
            self._start_date = start
        if self._end_date > end:
            self._end_date = end

    def buy(self, id, cash, date=None):
        shares = 0
        cost = 0
        if date is not None:
            currentPrice = self.getValueByDate(id, date, "close")
        else:
            currentPrice = self.getCurrentValue(id, "price")

        if self._commissionRatio != 0.0:
            shares = int(cash / (self._commissionRatio * currentPrice))
            cost = int(shares * currentPrice * self._commissionRatio)
        elif self._commissionCash != 0:
            shares = int((cash - self._commissionCash) / currentPrice)
            cost = int(shares * currentPrice + self._commissionCash)

        self._stocks[id]._shares += shares
        self._stocks[id]._cost += cost
        self._cash += cash - cost

    def sell(self, id, shares=None, date=None):
        if date is not None:
            currentPrice = self.getValueByDate(id, date, "close")
        else:
            currentPrice = self.getCurrentValue(id, "price")

        if shares is None:
            _shares = self._stocks[id]._shares
            self._stocks[id]._shares = 0

            if self._commissionRatio != 0.0:
                profit = int(
                    (shares * currentPrice * self._commissionRatio) * (1 - TAX_TAIWAN)
                )
            elif self._commissionCash != 0:
                profit = int(
                    (shares * currentPrice + self._commissionCash) * (1 - TAX_TAIWAN)
                )

            self._cash += profit

    def genFig(self, id, figName, plotList):
        fig, ax = self._stocks[id].plot(
            self._start_date, self._end_date, plotList, self._figures, figName
        )
        self._figures += 1

        return fig, ax

    def show(self):
        cursor = Cursor(plt.gca(), useblit=True, color="red", linewidth=1)
        plt.show()

    def getDateIterator(self, id):
        mask = (self._stocks[id]._price["date"] >= pd.to_datetime(self._start_date)) & (
            self._stocks[id]._price["date"] <= pd.to_datetime(self._end_date)
        )

        return self._stocks[id]._price.loc[mask, "date"].tolist()

    def exDividend(self, id):
        dividendStock = int(
            self._stocks[id]._dividendStock * self._stocks[id]._shares * 0.9809
        )
        dividendCash = int(
            self._stocks[id]._dividendCash * self._stocks[id]._shares * 0.9809
        )

        self._stocks[id]._accumulatedDividends += dividendCash
        self._stocks[id]._accumulatedStock += dividendStock
        self._stocks[id]._shares += dividendStock
        self._stocks[id]._asset += dividendCash

    def setCurrentValue(self, id, key, value):
        self._stocks[id]._current[key] = value

    def setValueByDate(self, id, date, key, value):
        self._stocks[id]._price.loc[
            self._stocks[id]._price["date"] == date, key
        ] = value

    def getValueByDate(self, id, date, key):
        df = self._stocks[id]._price
        filtered_df = df[df["date"] == date]
        if not filtered_df.empty:
            return filtered_df[key].values[0]
        else:
            return None

    def getDuration(self, id):
        df = self._stocks[id]._price
        df["date"] = pd.to_datetime(df["date"])
        return df.iloc[0]["date"], df.iloc[-1]["date"]

    def getShares(self, id):
        return self._stocks[id]._shares

    def getCosts(self, id):
        return self._stocks[id]._cost

    def getTotalDividends(self, id):
        return self._stocks[id]._accumulatedDividends

    def getNextDividendDay(self, id):
        return self._stocks[id].getNextDividendDay()

    def getCurrentValue(self, id, key):
        return self._stocks[id]._current[key]

    def updateInfo(self, id, date):
        self.setCurrentValue(id, "price", self.getValueByDate(id, date, "close"))

    def updateAsset(self, id, date):
        currentPrice = self.getCurrentValue(id, "price")
        duration = date - self._start_date

        dailyAsset = int(
            currentPrice * self._stocks[id]._shares + self._stocks[id]._asset
        )
        dailyCost = self._stocks[id]._cost
        if dailyCost == 0:
            ROI = 0
        else:
            ROI = (dailyAsset / dailyCost - 1) * 100

        if duration.days < 365 or dailyCost == 0:
            IRR = 0
        else:
            years = duration.days / 365.25
            IRR = (((dailyAsset / dailyCost) ** (1 / years)) - 1) * 100

        self.setCurrentValue(id, "DailyAsset", dailyAsset)
        self.setCurrentValue(id, "DailyCost", dailyCost)
        self.setCurrentValue(id, "ROI", ROI)
        self.setCurrentValue(id, "IRR", IRR)

        self.setValueByDate(id, date, "DailyAsset", dailyAsset)
        self.setValueByDate(id, date, "DailyCost", dailyCost)
        self.setValueByDate(id, date, "ROI", ROI)
        self.setValueByDate(id, date, "IRR", IRR)
