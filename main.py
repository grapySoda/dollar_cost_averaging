from backtest import Stock
from backtest import Dealer

import pandas as pd
import datetime
import os
import time

import matplotlib.pyplot as plt


# START_DATE = "1960-4-15"
# END_DATE = "2022-11-20"

START_DATE = "1960-4-15"
END_DATE = "2024-05-17"

# START_DATE = "2012-07-17"
# END_DATE = "2014-07-17"

# START_DATE = "2021-07-01"
# END_DATE = "2024-05-17"

# START_DATE = "2012-06-22"
# END_DATE = "2024-05-17"

# START_DATE = "2020-06-22"
# END_DATE = "2024-05-17"

MONTHLY_INVESTMENT = 36000
TOGET_STOCK = "0050"

if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    dealer = Dealer(token, START_DATE, END_DATE, commissionCash=1)
    dealer.add(TOGET_STOCK)

    date_iterator = dealer.getDateIterator(TOGET_STOCK)
    # date_iterator = date_iterator.date

    # start_time = time.time()
    # nextDividendDay = stock6208.getNextDividendDay(START_DATE)
    # stocks[TOGET_STOCK].plot(START_DATE, END_DATE)
    # nextDividendDay = stocks[TOGET_STOCK].getNextDividendDay(START_DATE)

    # dividendDate, dividendStock, dividendCash = dealer.getNextDividendDay(TOGET_STOCK)
    dividendDate = dealer.getNextDividendDay(TOGET_STOCK)
    prev_month = None
    lastDate = None
    for date in date_iterator:
        if dividendDate is not None:
            if date >= dividendDate:
                dealer.exDividend(TOGET_STOCK)
                dividendDate = dealer.getNextDividendDay(TOGET_STOCK)

        current_month = date.strftime("%Y-%m")
        if current_month != prev_month:
            prev_month = current_month
            dealer.buy(TOGET_STOCK, date, MONTHLY_INVESTMENT)

        dealer.updateInfo(TOGET_STOCK, date)

    # dealer.backtestEnd(TOGET_STOCK)

    print("dealer[006208]._shares: ", f"{dealer.getShares(TOGET_STOCK):,}")
    print("dealer[006208]._cost: ", f"{dealer.getCosts(TOGET_STOCK):,}")
    print(
        "dealer[006208]._accumulatedDividends: ",
        f"{dealer.getAccumulatedDividends(TOGET_STOCK):,}",
    )
    print(
        "Asset: ",
        f"{dealer.getLatestAsset(TOGET_STOCK):,}",
    )
    print("cash: ", f"{dealer._cash:,}")

    # plotList = ["close","5MA", "20MA", "60MA", "240MA", "DailyAsset"]
    plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    # dealer.plot(TOGET_STOCK, plotList)
    dealer.plot(TOGET_STOCK, plotList)

    plotList = ["DailyAsset", "DailyCost"]
    # plotList = ["DailyAsset"]
    # dealer.plot(TOGET_STOCK, plotList)
    dealer.plot(TOGET_STOCK, plotList)

    dealer.show()

    # if date == nextDividendDay:
    # print(
    #     "{}, {}".format(
    #         date, stocks[TOGET_STOCK].getDividendDatabaseTotalCash(date)
    #     )
    # )
    # nextDividendDay = stock6208.getNextDividendDay(date)
    # nextDividendDay = stocks[TOGET_STOCK].getNextDividendDay(date)

    # end_time = time.time()
    # print("Excution time：", end_time - start_time, " sec")
