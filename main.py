from backtest import Backtest


# START_DATE = "1960-4-15"
# END_DATE = "2022-11-20"

START_DATE = "1960-4-15"
END_DATE = "2024-11-20"

# START_DATE = "2004-4-15"
# END_DATE = "2008-11-20"

# START_DATE = "2008-4-15"
# END_DATE = "2011-05-17"

# START_DATE = "2008-4-15"
# END_DATE = "2014-05-17"

# START_DATE = "2008-4-15"
# END_DATE = "2024-11-20"

# START_DATE = "2008-4-15"
# END_DATE = "2018-11-20"

# START_DATE = "2010-4-15"
# END_DATE = "2018-11-20"

# START_DATE = "2010-4-15"
# END_DATE = "2020-11-20"

# START_DATE = "2012-07-17"
# END_DATE = "2014-07-17"

# START_DATE = "2021-07-01"
# END_DATE = "2024-05-17"

# START_DATE = "2012-06-22"
# END_DATE = "2024-05-17"

# START_DATE = "2021-01-22"
# END_DATE = "2022-01-17"

# START_DATE = "2020-06-22"
# END_DATE = "2024-05-17"

# MONTHLY_INVESTMENT = 36000
# COUNTRY = "tw"
# STOCK_ID = "0050"

# MONTHLY_INVESTMENT = 36000
# COUNTRY = "tw"
# STOCK_ID = "006208"

MONTHLY_INVESTMENT = 36000
COUNTRY = "us"
STOCK_ID = "QQQ"

def genPrice(dealer):
    plotName = "Price"
    plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    fig, ax = dealer.genFig(STOCK_ID, plotList, plotName)
    return fig, ax


if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    backtest = Backtest(token, START_DATE, END_DATE, commissionCash=1)
    backtest.add(COUNTRY, STOCK_ID)

    backtest.run()

    plotPriceList = ("Price", ["close"])
    plotDailyList = ("Daily", ["DailyAsset", "DailyCost"])
    plotBiosList = ("BIOS", ["5BIOS", "20BIOS", "60BIOS", "240BIOS"])
    plotRoiList = ("ROI", ["ROI"])
    plotIrrList = ("IRR", ["IRR"])

    backtest.addTab("Price", plotPriceList)
    backtest.addTab("Accumulated Asset", plotPriceList, plotDailyList)
    backtest.addTab("BIOS", plotPriceList, plotBiosList)
    backtest.addTab("ROI", plotPriceList, plotRoiList)
    backtest.addTab("IRR", plotPriceList, plotIrrList)

    backtest.printResult()

    backtest.show()
