from backtest import Stock
from backtest import Dealer
from backtest import Window

import pandas as pd
import datetime
import os
import time

import matplotlib.pyplot as plt


# START_DATE = "1960-4-15"
# END_DATE = "2022-11-20"

# START_DATE = "1960-4-15"
# END_DATE = "2024-11-20"

# START_DATE = "2004-4-15"
# END_DATE = "2008-11-20"

# START_DATE = "2008-4-15"
# END_DATE = "2011-05-17"

# START_DATE = "2012-07-17"
# END_DATE = "2014-07-17"

# START_DATE = "2021-07-01"
# END_DATE = "2024-05-17"

# START_DATE = "2012-06-22"
# END_DATE = "2024-05-17"

START_DATE = "2021-01-22"
END_DATE = "2022-01-17"

# START_DATE = "2020-06-22"
# END_DATE = "2024-05-17"

MONTHLY_INVESTMENT = 36000
# TOGET_STOCK = "0050"
TOGET_STOCK = "006208"

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

    dividendDate = dealer.getNextDividendDay(TOGET_STOCK)
    prev_month = None
    lastDate = None
    for date in date_iterator:
        dealer.updateInfo(TOGET_STOCK, date)
        if dividendDate is not None:
            if date >= dividendDate:
                dealer.exDividend(TOGET_STOCK)
                dividendDate = dealer.getNextDividendDay(TOGET_STOCK)

        current_month = date.strftime("%Y-%m")
        if current_month != prev_month:
            prev_month = current_month
            # dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT, date)
            dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT)
        dealer.updateAsset(TOGET_STOCK, date)

    print("dealer[006208]._shares: ", f"{dealer.getShares(TOGET_STOCK):,}")
    print("dealer[006208]._cost: ", f"{dealer.getCosts(TOGET_STOCK):,}")
    print(
        "dealer[006208]._accumulatedDividends: ",
        f"{dealer.getAccumulatedDividends(TOGET_STOCK):,}",
    )
    _asset = dealer.getCurrentValue(TOGET_STOCK, "DailyAsset")
    print(
        "Asset: ",
        f"{_asset:,}",
    )
    print("cash: ", f"{dealer._cash:,}")

    window = Window("Matplotlib with Tabs")
    # plotList = ["close","5MA", "20MA", "60MA", "240MA", "DailyAsset", "DailyCost", "ROI", "5BIOS", "20BIOS", "60BIOS", "240BIOS"]
    plotName = "Price"
    plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    fig1, ax1 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    window.addTab(plotName, fig1, ax1)

    plotName = "Accumulated Asset"
    plotList = ["DailyAsset", "DailyCost"]
    fig2, ax2 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    window.addTab(plotName, fig2, ax2)

    plotName = "BIOS"
    plotList = ["5BIOS", "20BIOS", "60BIOS", "240BIOS"]
    fig3, ax3 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    window.addTab(plotName, fig3, ax3)

    plotName = "ROI"
    plotList = ["ROI"]
    fig4, ax4 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    window.addTab(plotName, fig4, ax4)

    window.show()
