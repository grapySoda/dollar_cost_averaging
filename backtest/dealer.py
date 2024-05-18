from .stock import Stock
import pandas as pd


class Dealer:

    def __init__(
        self, token, strat_date, end_date, commissionRatio=0.0, commissionCash=0
    ):
        self._cash = 0
        self._stocks = {}
        self._token = token
        self._strat_date = strat_date
        self._end_date = end_date
        self._commissionRatio = commissionRatio
        self._commissionCash = commissionCash

    def add(self, id):
        self._stocks[id] = Stock(id, self._token)

    def buy(self, id, shares):
        if self.commissionRatio != 0.0:
            cost = self._token * self._latestClosePrice * self.commissionRatio
        elif self.commissionCash != 0:
            cost = self._token * self._latestClosePrice + self.commissionCash

        self._stocks[id]._shares += shares
        self._stocks[id]._cost += cost
        return False

    def sell(self, path):
        return False

    def plot(self, id):
        self._stocks[id].plot(self._strat_date, self._end_date)

    def getClosePrice(self, id, date):
        df = self._stocks[id]._price
        filtered_df = df[df["date"] == date]
        if not filtered_df.empty:
            self._latestClosePrice = filtered_df["close"].values[0]
            return self._latestClosePrice
        else:
            return None
