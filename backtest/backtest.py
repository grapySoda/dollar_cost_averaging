from .window import Window
from .dealer import Dealer

import time
from qbstyles import mpl_style

mpl_style(True)
MONTHLY_INVESTMENT = 36000


class Backtest:

    def __init__(
        self, token, strat_date, end_date, commissionRatio=0.0, commissionCash=0
    ):
        self._window = Window("Backtest")
        self._dealer = Dealer(
            token, strat_date, end_date, commissionRatio, commissionCash
        )

    def add(self, stock):
        self._stock = stock
        self._dealer.add(stock)
        self._date_iterator = self._dealer.getDateIterator(stock)
        self._dividendDate = self._dealer.getNextDividendDay(stock)

    def run(self):
        start_time = time.time()
        prev_month = None
        for date in self._date_iterator:
            self._dealer.updateInfo(self._stock, date)
            if self._dividendDate is not None:
                if date >= self._dividendDate:
                    self._dealer.exDividend(self._stock)
                    self._dividendDate = self._dealer.getNextDividendDay(self._stock)

            current_month = date.strftime("%Y-%m")
            if current_month != prev_month:
                prev_month = current_month
                # dealer.buy(TOGET_STOCK, MONTHLY_INVESTMENT, date)
                self._dealer.buy(self._stock, MONTHLY_INVESTMENT)
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
        print("{:<16} {:<16}".format("Excution time:", f"{self._execution_time:,}"))
        print("{:<16} {:<16}".format("Total shares:", self.getTotalShares()))
        print("{:<16} {:<16}".format("Total cost:", self.getTotalCosts()))
        print("{:<16} {:<16}".format("Total Dividends:", self.getTotalDividends()))
        print("{:<16} {:<16}".format("Total Asset:", self.getTotalAsset()))

    def getTotalAsset(self):
        _asset = self._dealer.getCurrentValue(self._stock, "DailyAsset")
        return f"{_asset:,}"

    def getTotalShares(self):
        return f"{self._dealer.getShares(self._stock):,}"

    def getTotalCosts(self):
        return f"{self._dealer.getCosts(self._stock):,}"

    def getTotalDividends(self):
        return f"{self._dealer.getTotalDividends(self._stock):,}"
