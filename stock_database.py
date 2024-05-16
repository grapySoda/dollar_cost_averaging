import os
import datetime
import pandas as pd
from FinMind.data import DataLoader


class StockDatabase:

    def __init__(self, stock_id, token):
        self._startDate = datetime.date(1960, 4, 15)
        self._endDate = datetime.date.today()
        self._stock_id = stock_id
        self._api = DataLoader()
        self._api.login_by_token(api_token=token)

        self.getStockDividend()

    def str2date(self, date_str):
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def isSendDividendToday(self, input_date):
        self._stockDividend["date"] = pd.to_datetime(self._stockDividend["date"])
        if input_date in self._stockDividend["date"].astype(str).values:
            print("Send")
            return True
        else:
            return False

    def getNextDividendDay(self, input_date):
        _input_date = pd.to_datetime(input_date)

        next_date = self._stockDividend[self._stockDividend["date"] > _input_date][
            "date"
        ].min()

        if pd.isnull(next_date):
            return None

        return self.str2date(next_date.strftime("%Y-%m-%d"))

    def getDividendTotalCash(self, input_date):
        _input_date = pd.to_datetime(input_date)

        closest_date_index = self._stockDividend["date"].sub(_input_date).abs().idxmin()
        closest_date_row = self._stockDividend.loc[closest_date_index]

        if closest_date_row["date"] != _input_date:
            # next_date_row = self._stockDividend.loc[
            #     self._stockDividend["date"] > _input_date
            # ].iloc[0]
            # return next_date_row["TotalCash"]
            return 0.0
        else:
            return closest_date_row["TotalCash"]

    def getStockDividend(self):
        name = "taiwan_stock_dividend"
        filePath = "database/{}/{}.csv".format(name, self._stock_id)

        if os.path.exists(filePath):
            print("Find {}".format(filePath))
            self._stockDividend = pd.read_csv(filePath)
            self._stockDividend["date"] = pd.to_datetime(self._stockDividend["date"])
        else:
            print("Start to download {}".format(filePath))
            self._stockDividend = self._api.taiwan_stock_dividend(
                stock_id=self._stock_id,
                start_date=self._startDate,
            )

            self._stockDividend["TotalStock"] = (
                self._stockDividend["StockEarningsDistribution"]
                + self._stockDividend["StockStatutorySurplus"]
            )
            self._stockDividend["TotalCash"] = (
                self._stockDividend["CashEarningsDistribution"]
                + self._stockDividend["CashStatutorySurplus"]
            )
            self._stockDividend = self._stockDividend[
                [
                    "date",
                    "stock_id",
                    "CashDividendPaymentDate",
                    "TotalStock",
                    "TotalCash",
                ]
            ]
            self._stockDividend["date"] = pd.to_datetime(self._stockDividend["date"])

            if not os.path.exists("database/{}".format(name)):
                os.makedirs("database/{}".format(name))
            self._stockDividend.to_csv(
                "database/{}/{}.csv".format("taiwan_stock_dividend", self._stock_id),
                index=False,
            )
