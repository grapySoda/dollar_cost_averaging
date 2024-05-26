from .window import Window
from .dealer import Dealer
import matplotlib.pyplot as plt
import time
import matplotx

plt.style.use(matplotx.styles.dracula)

MONTHLY_INVESTMENT = 36000
TAX_TAIWAN = 0.003


class Backtest:

    def __init__(
        self, token, start_date, end_date, commissionRatio=0.0, commissionCash=0
    ):
        self._window = Window("Backtest")
        self._dealer = Dealer(
            token, start_date, end_date, commissionRatio, commissionCash
        )

    def add(self, stock):
        self._stock = stock
        self._dealer.add(stock)
        self._date_iterator = self._dealer.getDateIterator(stock)
        self._dividendDate = self._dealer.getNextDividendDay(stock)
        # start, end = self._dealer.getDuration(stock)
        duration = self._dealer._end_date - self._dealer._start_date
        self._years = duration.days / 365.25

    def run(self):
        start_time = time.time()
        prev_month = None
        for date in self._date_iterator:
            self._dealer.updateInfo(self._stock, date)
            if self._dividendDate is not None:
                if date >= self._dividendDate:
                    self._dealer.exDividend(self._stock)
                    self._dividendDate = self._dealer.getNextDividendDay(self._stock)

            ### Strategy 01
            current_month = date.strftime("%Y-%m")
            if current_month != prev_month:
                prev_month = current_month
                # self._dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT, date)
                self._dealer.buy(self._stock, MONTHLY_INVESTMENT)

            ### Strategy 02

            self._dealer.updateAsset(self._stock, date)

        end_time = time.time()
        self._execution_time = end_time - start_time

    def show(self):
        self._window.show()

    def addTab(self, tabName, plotList1, plotList2=None):
        if plotList2:
            name1, list1 = plotList1
            name2, list2 = plotList2
            fig1, ax1 = self._dealer.genFig(self._stock, name1, list1)
            fig2, ax2 = self._dealer.genFig(self._stock, name2, list2)
            self._window.addTab(tabName, fig1, ax1, fig2, ax2)
        else:
            name1, list1 = plotList1
            fig, ax = self._dealer.genFig(self._stock, name1, list1)
            self._window.addTab(tabName, fig, ax)

    def printResult(self):
        roi = f"{self.getRoi():,}"
        irr = f"{self.getIrr():,}"
        asset = f"{int(self.getTotalAsset()*(1-TAX_TAIWAN)):,}"
        dividends = f"{int(self.getTotalDividends()):,}"
        costs = f"{int(self.getTotalCosts()):,}"
        tax = f"{int(self.getTotalAsset()*TAX_TAIWAN):,}"
        shares = f"{int(self.getTotalShares()):,}"
        years = f"{round(float(self._years), 2):,}"
        elapsed = f"{round(float(self._execution_time), 2):,}"

        print("{:<16} {:>11}".format("Stock:", self._stock))
        print(
            "{:<16} {:>11}".format(
                "Start date:", "{}".format(self._dealer._start_date.date())
            )
        )
        print(
            "{:<16} {:>11}".format(
                "End date:", "{}".format(self._dealer._end_date.date())
            )
        )
        print("{:<16} {:>11} %".format("ROI:", roi))
        print("{:<16} {:>11} %".format("IRR:", irr))
        print("{:<16} {:>11} NTD".format("Total asset:", asset))
        print("{:<16} {:>11} NTD".format("Total dividends:", dividends))
        print("{:<16} {:>11} NTD".format("Total costs:", costs))
        print("{:<16} {:>11} NTD".format("Total tax:", tax))
        print("{:<16} {:>11} shares".format("Total shares:", shares))
        print("{:<16} {:>11} years".format("Duration:", years))
        print("{:<16} {:>11} seconds".format("Elapsed time:", elapsed))

    def getRoi(self):
        return round(
            float(
                (self.getTotalAsset() - self.getTotalCosts())
                / self.getTotalCosts()
                * 100
            ),
            2,
        )

    def getIrr(self):
        return round(
            float(
                (
                    ((self.getTotalAsset() / self.getTotalCosts()) ** (1 / self._years))
                    - 1
                )
                * 100
            ),
            2,
        )

    def getTotalAsset(self):
        return round(float(self._dealer.getCurrentValue(self._stock, "DailyAsset")), 2)

    def getTotalShares(self):
        return round(float(self._dealer.getShares(self._stock)), 2)

    def getTotalCosts(self):
        return round(float(self._dealer.getCosts(self._stock)), 2)

    def getTotalDividends(self):
        return round(float(self._dealer.getTotalDividends(self._stock)), 2)
