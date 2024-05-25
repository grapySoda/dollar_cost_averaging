from .stock import Stock
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


class Dealer:

    def __init__(
        self, token, strat_date, end_date, commissionRatio=0.0, commissionCash=0
    ):
        self._figures = 1
        self._cash = 0
        self._stocks = {}
        self._token = token
        self._strat_date = strat_date
        self._end_date = end_date
        if commissionRatio > 1.0 or commissionRatio == 0.0:
            self._commissionRatio = commissionRatio
        else:
            self._commissionRatio = 1 + commissionRatio
        self._commissionCash = commissionCash

    def add(self, id):
        self._stocks[id] = Stock(id, self._token)

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

    def sell(self, path):
        return False

    def genFig(self, id, plotList, figName):
        fig, ax = self._stocks[id].plot(
            self._strat_date, self._end_date, plotList, self._figures, figName
        )
        self._figures += 1

        return fig, ax

    def show(self):
        cursor = Cursor(plt.gca(), useblit=True, color="red", linewidth=1)
        plt.show()

    def getDateIterator(self, id):
        mask = (self._stocks[id]._price["date"] >= pd.to_datetime(self._strat_date)) & (
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

    def getShares(self, id):
        return self._stocks[id]._shares

    def getCosts(self, id):
        return self._stocks[id]._cost

    def getAccumulatedDividends(self, id):
        return self._stocks[id]._accumulatedDividends

    def getNextDividendDay(self, id):
        return self._stocks[id].getNextDividendDay()

    def getCurrentValue(self, id, key):
        return self._stocks[id]._current[key]

    def updateInfo(self, id, date):
        self.setCurrentValue(id, "price", self.getValueByDate(id, date, "close"))

        self.setCurrentValue(id, "5MA", self.getValueByDate(id, date, "5MA"))
        self.setCurrentValue(id, "20MA", self.getValueByDate(id, date, "20MA"))
        self.setCurrentValue(id, "60MA", self.getValueByDate(id, date, "60MA"))
        self.setCurrentValue(id, "240MA", self.getValueByDate(id, date, "240MA"))

        self.setCurrentValue(id, "5BIOS", self.getValueByDate(id, date, "5BIOS"))
        self.setCurrentValue(id, "20BIOS", self.getValueByDate(id, date, "20BIOS"))
        self.setCurrentValue(id, "60BIOS", self.getValueByDate(id, date, "60BIOS"))
        self.setCurrentValue(id, "240BIOS", self.getValueByDate(id, date, "240BIOS"))

    def updateAsset(self, id, date):
        currentPrice = self.getCurrentValue(id, "price")

        dailyAsset = int(
            currentPrice * self._stocks[id]._shares + self._stocks[id]._asset
        )
        dailyCost = self._stocks[id]._cost
        ROI = (dailyAsset / dailyCost - 1) * 100

        self.setCurrentValue(id, "DailyAsset", dailyAsset)
        self.setCurrentValue(id, "DailyCost", dailyCost)
        self.setCurrentValue(id, "ROI", ROI)

        self.setValueByDate(id, date, "DailyAsset", dailyAsset)
        self.setValueByDate(id, date, "DailyCost", dailyCost)
        self.setValueByDate(id, date, "ROI", ROI)
