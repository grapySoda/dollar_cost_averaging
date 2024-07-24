import os
import datetime
import requests
import pandas as pd
from FinMind.data import DataLoader
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


class LimitedArray:
    def __init__(self, max_size):
        self.window = []
        self.ma = []
        self.bios = []
        self.max_size = max_size

    def push(self, value):
        _value = 0
        if len(self.window) == self.max_size:
            self.window.pop(0)
        self.window.append(value)

        if len(self.window) < self.max_size:
            self.ma.append(value)
            _value = value
        else:
            num = sum(self.window) / self.max_size
            num_str = f"{num:.2f}"
            self.ma.append(num_str)
            _value = num

        _bios = (value / _value - 1) * 100
        self.bios.append(_bios)


class Stock:

    def __init__(self, country, id, token):
        self._start_date = datetime.date(1960, 4, 15)
        self._end_date = datetime.date.today()
        self._id = id
        self._country = country
        self._api = DataLoader()
        self._api.login_by_token(api_token=token)
        self._dailyAsset = []
        self._token = token
        self._asset = 0
        self._cost = 0
        self._shares = 0
        self._dividendIndex = 0
        self._dividendStock = None
        self._dividendCash = None
        self._accumulatedDividends = 0
        self._accumulatedStock = 0

        self._current = {}

        self.getPriceDatabase()
        self.getDividendDatabase()

    def plot(self, start_date, end_date, plotList, figureIdx, figName="Stock Data"):
        mask = (self._price["date"] >= start_date) & (self._price["date"] <= end_date)
        df_filtered = self._price.loc[mask]

        df_filtered.dropna(subset=plotList, how="all", inplace=True)

        fig, ax = plt.subplots(figsize=(12, 6), num=figureIdx)

        for label in plotList:
            ax.plot(df_filtered["date"], df_filtered[label], label=label, linewidth=1)

        ax.set_title(figName)
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()

        def thousands_formatter(x, pos):
            return f"{x:,.0f}"

        ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        ax.grid(True)

        return fig, ax

    def str2date(self, date_str):
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def isSendDividendToday(self, input_date):
        self._dividend["date"] = pd.to_datetime(self._dividend["date"])
        if input_date in self._dividend["date"].astype(str).values:
            return True
        else:
            return False

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

        return (
            _5ma.ma,
            _20ma.ma,
            _60ma.ma,
            _240ma.ma,
            _5ma.bios,
            _20ma.bios,
            _60ma.bios,
            _240ma.bios,
        )

    def getPriceDatabase(self):
        name = "taiwan_stock_daily"
        filePath = "database/{}/{}.csv".format(name, self._id)

        if os.path.exists(filePath):
            print("Find {}".format(filePath))
            self._price = pd.read_csv(filePath)
            self._price["date"] = pd.to_datetime(self._price["date"])
        else:
            print("Start to download {}".format(filePath))
            if (self._country == "tw" or self._country == "TW"):
                self._price = self._api.taiwan_stock_daily(
                    stock_id=self._id,
                    start_date=self._start_date,
                    end_date=self._end_date,
                )
            elif (self._country == "us" or self._country == "US"):
                url = 'https://api.finmindtrade.com/api/v4/data'
                parameter = {
                    "dataset": "USStockPrice",
                    "data_id": self._id,
                    "start_date": self._start_date,
                    "end_date": self._end_date,
                    "token": self._token,
                }
                data = requests.get(url, params=parameter)
                data = data.json()
                self._price = pd.DataFrame(data['data'])

            ### remove the empty price
            self._price = self._price[self._price["close"] != 0]
            self._price["date"] = pd.to_datetime(self._price["date"])

            (
                self._price["5MA"],
                self._price["20MA"],
                self._price["60MA"],
                self._price["240MA"],
                self._price["5BIOS"],
                self._price["20BIOS"],
                self._price["60BIOS"],
                self._price["240BIOS"],
            ) = self.getMovingAverage(self._price)

            if not os.path.exists("database/{}".format(name)):
                os.makedirs("database/{}".format(name))
            self._price.to_csv(
                "database/{}/{}.csv".format(name, self._id),
                index=False,
            )

        self._price["DailyAsset"] = 0
        self._price["DailyCost"] = 0
        self._price["ROI"] = 0.0

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
