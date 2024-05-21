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
        if commissionRatio > 1.0 or commissionRatio == 0.0:
            self._commissionRatio = commissionRatio
        else:
            self._commissionRatio = 1 + commissionRatio
        self._commissionCash = commissionCash

    def add(self, id):
        self._stocks[id] = Stock(id, self._token)

    def buy(self, id, date, cash):
        shares = 0
        cost = 0
        currentPrice = self.getClosePrice(id, date)
        if self._commissionRatio != 0.0:
            shares = int(cash / (self._commissionRatio * currentPrice))
            cost = int(shares * currentPrice * self._commissionRatio)
        elif self._commissionCash != 0:
            shares = int((cash - self._commissionCash) / currentPrice)
            cost = int(shares * currentPrice + self._commissionCash)

        self._stocks[id]._shares += shares
        self._stocks[id]._cost += cost
        self._cash += cash - cost
        return False

    def sell(self, path):
        return False

    def plot(self, id, plotList):
        self._stocks[id].plot(self._strat_date, self._end_date, plotList)

    def getClosePrice(self, id, date):
        df = self._stocks[id]._price
        filtered_df = df[df["date"] == date]
        if not filtered_df.empty:
            return filtered_df["close"].values[0]
        else:
            return None

    def getDateIterator(self, id):
        mask = (self._stocks[id]._price["date"] >= pd.to_datetime(self._strat_date)) & (
            self._stocks[id]._price["date"] <= pd.to_datetime(self._end_date)
        )

        return self._stocks[id]._price.loc[mask, "date"].tolist()

    # def updateInfo(self, id):
