from backtest import Stock
from backtest import Dealer
from backtest import Window
from backtest import Backtest

import pandas as pd
from qbstyles import mpl_style
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
TOGET_STOCK = "0050"
# TOGET_STOCK = "006208"


def genPrice(dealer):
    plotName = "Price"
    plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    fig, ax = dealer.genFig(TOGET_STOCK, plotList, plotName)
    return fig, ax


if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    mpl_style(True)
    # plt.style.use(
    #     "https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle"
    # )

    backtest = Backtest(token, START_DATE, END_DATE, commissionCash=1)

    # dealer = Dealer(token, START_DATE, END_DATE, commissionCash=1)
    # dealer.add(TOGET_STOCK)

    # date_iterator = dealer.getDateIterator(TOGET_STOCK)

    # dividendDate = dealer.getNextDividendDay(TOGET_STOCK)
    # prev_month = None
    # lastDate = None
    backtest.add("006208")
    # start_time = time.time()
    backtest.run()
    # for date in date_iterator:
    #     dealer.updateInfo(TOGET_STOCK, date)
    #     if dividendDate is not None:
    #         if date >= dividendDate:
    #             dealer.exDividend(TOGET_STOCK)
    #             dividendDate = dealer.getNextDividendDay(TOGET_STOCK)

    #     current_month = date.strftime("%Y-%m")
    #     if current_month != prev_month:
    #         prev_month = current_month
    #         # dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT, date)
    #         dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT)
    #     dealer.updateAsset(TOGET_STOCK, date)

    # end_time = time.time()
    # execution_time_ms = end_time - start_time
    backtest.printResult()
    # print(f"Excution time: {execution_time_ms:.2f} s")

    # print("dealer[006208]._shares: ", backtest.getTotalShares())
    # print("dealer[006208]._cost: ", backtest.getTotalCosts())
    # print(
    #     "dealer[006208]._accumulatedDividends: ",
    #     backtest.getTotalDividends(),
    # )
    # print("Asset: ", f"{backtest.getTotalAsset():,}")
    # print("dealer[006208]._shares: ", f"{dealer.getShares(TOGET_STOCK):,}")
    # print("dealer[006208]._cost: ", f"{dealer.getCosts(TOGET_STOCK):,}")
    # print(
    #     "dealer[006208]._accumulatedDividends: ",
    #     f"{dealer.getTotalDividends(TOGET_STOCK):,}",
    # )
    # _asset = dealer.getCurrentValue(TOGET_STOCK, "DailyAsset")
    # print("Asset: ", f"{_asset:,}")
    # print("cash: ", f"{dealer._cash:,}")

    # window = Window("Matplotlib with Tabs")
    # plotList = ["close","5MA", "20MA", "60MA", "240MA", "DailyAsset", "DailyCost", "ROI", "5BIOS", "20BIOS", "60BIOS", "240BIOS"]
    # plotName = "Price"
    # plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    # fig1, ax1 = dealer.genFig(TOGET_STOCK, plotList, plotName)

    plotPriceList = ("Price", ["close"])
    plotDailyList = ("Daily", ["DailyAsset", "DailyCost"])
    plotBiosList = ("BIOS", ["5BIOS", "20BIOS", "60BIOS", "240BIOS"])
    plotRoiList = ("ROI", ["ROI"])

    backtest.addTab("Price", plotPriceList)
    backtest.addTab("Accumulated Asset", plotPriceList, plotDailyList)
    backtest.addTab("BIOS", plotPriceList, plotBiosList)
    backtest.addTab("ROI", plotPriceList, plotRoiList)

    # plotName = "Price"
    # fig1, ax1 = genPrice(dealer)
    # window.addTab(plotName, fig1, ax1)

    # plotName = "Accumulated Asset"
    # plotList = ["DailyAsset", "DailyCost"]
    # fig2, ax2 = genPrice(dealer)
    # fig22, ax22 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    # window.addTab(plotName, fig2, ax2, fig22, ax22)

    # plotName = "BIOS"
    # plotList = ["5BIOS", "20BIOS", "60BIOS", "240BIOS"]
    # fig3, ax3 = genPrice(dealer)
    # fig33, ax33 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    # window.addTab(plotName, fig3, ax3, fig33, ax33)

    # plotName = "ROI"
    # plotList = ["ROI"]
    # fig4, ax4 = genPrice(dealer)
    # fig44, ax44 = dealer.genFig(TOGET_STOCK, plotList, plotName)
    # window.addTab(plotName, fig4, ax4, fig44, ax44)
    backtest.show()
    # window.show()
