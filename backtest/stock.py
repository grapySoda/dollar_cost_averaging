import os
import datetime
import pandas as pd
from FinMind.data import DataLoader
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Cursor


class LimitedArray:
    def __init__(self, max_size):
        self.window = []
        self.array = []
        self.max_size = max_size

    def push(self, value):
        if len(self.window) == self.max_size:
            self.window.pop(0)
        self.window.append(value)

        if len(self.window) < self.max_size:
            # self.array.append(0)
            self.array.append(value)
        else:
            num = sum(self.window) / self.max_size
            num = f"{num:.2f}"
            self.array.append(num)


class Stock:

    def __init__(self, id, token):
        self._start_date = datetime.date(1960, 4, 15)
        self._end_date = datetime.date.today()
        self._id = id
        self._api = DataLoader()
        self._api.login_by_token(api_token=token)
        self._dailyAsset = []
        self._asset = 0
        self._cost = 0
        self._shares = 0
        self._dividendIndex = 0
        self._dividendStock = None
        self._dividendCash = None
        self._accumulatedDividends = 0
        self._accumulatedStock = 0

        self.getPriceDatabase()
        self.getDividendDatabase()

    def plot(self, start_date, end_date, plotList, figureIdx):
        mask = (self._price["date"] >= start_date) & (self._price["date"] <= end_date)
        df_filtered = self._price.loc[mask]

        df_filtered.dropna(subset=plotList, how="all", inplace=True)

        plt.figure(figureIdx, figsize=(12, 6))

        for label in plotList:
            plt.plot(df_filtered["date"], df_filtered[label], label=label, linewidth=1)

        plt.title("Stock Data")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()

        def thousands_formatter(x, pos):
            return f"{x:,.0f}"

        plt.gca().yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        plt.grid(True)
        # plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    def str2date(self, date_str):
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def isSendDividendToday(self, input_date):
        self._dividend["date"] = pd.to_datetime(self._dividend["date"])
        if input_date in self._dividend["date"].astype(str).values:
            return True
        else:
            return False

    # def getNextDividendDay(self, input_date):
    #     _input_date = pd.to_datetime(input_date)

    #     next_date = self._dividend[self._dividend["date"] > _input_date]["date"].min()

    #     if pd.isnull(next_date):
    #         return None

    #     return self.str2date(next_date.strftime("%Y-%m-%d"))

    def getNextDividendDay(self):
        if self._dividendIndex < len(self._dividend):
            row = self._dividend.iloc[self._dividendIndex]
            self._dividendIndex += 1
            self._dividendStock = row["TotalStock"]
            self._dividendCash = row["TotalCash"]
            return row["date"]
        else:
            return None  # No more dates available

    def getDividendDatabaseTotalCash(self, input_date):
        _input_date = pd.to_datetime(input_date)

        closest_date_index = self._dividend["date"].sub(_input_date).abs().idxmin()
        closest_date_row = self._dividend.loc[closest_date_index]

        if closest_date_row["date"] != _input_date:
            # next_date_row = self._dividend.loc[
            #     self._dividend["date"] > _input_date
            # ].iloc[0]
            # return next_date_row["TotalCash"]
            return 0.0
        else:
            return closest_date_row["TotalCash"]

    def getMovingAverage(self, price):
        _5ma = LimitedArray(5)
        _20ma = LimitedArray(20)
        _60ma = LimitedArray(60)
        _240ma = LimitedArray(240)

        maList = [_5ma, _20ma, _60ma, _240ma]
        closeList = price["close"].tolist()

        for close in closeList:
            for ma in maList:
                ma.push(close)

        return _5ma.array, _20ma.array, _60ma.array, _240ma.array

    def getPriceDatabase(self):
        name = "taiwan_stock_daily"
        filePath = "database/{}/{}.csv".format(name, self._id)

        if os.path.exists(filePath):
            print("Find {}".format(filePath))
            self._price = pd.read_csv(filePath)
            self._price["date"] = pd.to_datetime(self._price["date"])
        else:
            print("Start to download {}".format(filePath))
            self._price = self._api.taiwan_stock_daily(
                stock_id=self._id,
                start_date=self._start_date,
                end_date=self._end_date,
            )

            ### remove the empty price
            self._price = self._price[self._price["close"] != 0]
            self._price["date"] = pd.to_datetime(self._price["date"])

            (
                self._price["5MA"],
                self._price["20MA"],
                self._price["60MA"],
                self._price["240MA"],
            ) = self.getMovingAverage(self._price)

            self._price["DailyAsset"] = 0
            self._price["DailyCost"] = 0
            self._price["ROI"] = 0

            if not os.path.exists("database/{}".format(name)):
                os.makedirs("database/{}".format(name))
            self._price.to_csv(
                "database/{}/{}.csv".format(name, self._id),
                index=False,
            )

    def getDividendDatabase(self):
        name = "taiwan_stock_dividend"
        filePath = "database/{}/{}.csv".format(name, self._id)

        if os.path.exists(filePath):
            print("Find {}".format(filePath))
            self._dividend = pd.read_csv(filePath)
            self._dividend["date"] = pd.to_datetime(self._dividend["date"])
        else:
            print("Start to download {}".format(filePath))
            self._dividend = self._api.taiwan_stock_dividend(
                stock_id=self._id,
                start_date=self._start_date,
            )

            self._dividend["TotalStock"] = (
                self._dividend["StockEarningsDistribution"]
                + self._dividend["StockStatutorySurplus"]
            )
            self._dividend["TotalCash"] = (
                self._dividend["CashEarningsDistribution"]
                + self._dividend["CashStatutorySurplus"]
            )
            self._dividend = self._dividend[
                [
                    "date",
                    "stock_id",
                    "CashDividendPaymentDate",
                    "TotalStock",
                    "TotalCash",
                ]
            ]
            self._dividend["date"] = pd.to_datetime(self._dividend["date"])

            if not os.path.exists("database/{}".format(name)):
                os.makedirs("database/{}".format(name))
            self._dividend.to_csv(
                "database/{}/{}.csv".format(name, self._id),
                index=False,
            )
