import os
import datetime
import pandas as pd
from FinMind.data import DataLoader

START_DATE = datetime.date(1960, 4, 15)
END_DATE = datetime.date.today()


class StockDatabase:

    def __init__(self, stock_id, token):
        self._stock_id = stock_id
        self._api = DataLoader()
        self._api.login_by_token(api_token=token)

        self.getStockDividend()

    def isFileExist(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def getStockDividend(self):
        name = "taiwan_stock_dividend"
        filePath = "database/{}/{}.csv".format(name, self._stock_id)

        if os.path.exists(filePath):
            print("Find {}".format(filePath))
            self._stockDividend = pd.read_csv(filePath)
        else:
            print("Start to download {}".format(filePath))
            self._stockDividend = self._api.taiwan_stock_dividend(
                stock_id=self._stock_id,
                start_date=START_DATE,
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

            if not os.path.exists(name):
                os.makedirs(name)
            self._stockDividend.to_csv(
                "database/{}/{}.csv".format("taiwan_stock_dividend", self._stock_id),
                index=False,
            )
