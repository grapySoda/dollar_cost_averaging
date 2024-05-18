from backtest.stock_database import StockDatabase

# from backtest import Backtest

import pandas as pd
import datetime
import os
import time

# START_DATE = "1960-4-15"
# END_DATE = "2022-11-20"

START_DATE = "2012-07-17"
END_DATE = "2024-05-17"

if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    stocks = {}
    stocks["006208"] = StockDatabase("006208", token)
    # stock6208 = StockDatabase("006208", token)

    date_iterator = pd.date_range(start=START_DATE, end=END_DATE, normalize=True)
    date_iterator = date_iterator.date

    # start_time = time.time()
    # nextDividendDay = stock6208.getNextDividendDay(START_DATE)
    nextDividendDay = stocks["006208"].getNextDividendDay(START_DATE)
    stocks["006208"].plot(START_DATE, END_DATE)

    # for date in date_iterator:

    #     if date == nextDividendDay:
    #         # print(
    #         #     "{}, {}".format(
    #         #         date, stocks["006208"].getDividendDatabaseTotalCash(date)
    #         #     )
    #         # )
    #         # nextDividendDay = stock6208.getNextDividendDay(date)
    #         nextDividendDay = stocks["006208"].getNextDividendDay(date)

    # end_time = time.time()
    # print("Excution time：", end_time - start_time, " sec")
