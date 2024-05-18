# from .stock import Stock
from .dealer import Dealer
import pandas as pd


class Backtest:

    def __init__(self, start_date, end_date, token):
        self._dealer = Dealer(token)
        self._dates = self.getDates(start_date, end_date)

    def getDates(self, start_date, end_date):
        date_iterator = pd.date_range(start=start_date, end=end_date, normalize=True)
        return date_iterator.date

    def run(self):
        return False

    def updateDatabase(self):
        return False
