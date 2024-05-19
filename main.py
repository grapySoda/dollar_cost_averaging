from backtest import Stock
from backtest import Dealer

import pandas as pd
import datetime
import os
import time

# START_DATE = "1960-4-15"
# END_DATE = "2022-11-20"

START_DATE = "2012-07-17"
END_DATE = "2014-07-17"
MONTHLY_INVESTMENT = 36000

if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    dealer = Dealer(token, START_DATE, END_DATE)
    dealer.add("006208")

    date_iterator = dealer.getDateIterator("006208")
    # date_iterator = date_iterator.date

    # start_time = time.time()
    # nextDividendDay = stock6208.getNextDividendDay(START_DATE)
    # nextDividendDay = stocks["006208"].getNextDividendDay(START_DATE)
    # stocks["006208"].plot(START_DATE, END_DATE)
    prev_month = None
    for date in date_iterator:
        current_month = date.strftime("%Y-%m")
        if current_month != prev_month:
            prev_month = current_month
            dealer.buy("006208", date, MONTHLY_INVESTMENT)

        # dealer.updateInfo("006208")

        # if date == nextDividendDay:
        # print(
        #     "{}, {}".format(
        #         date, stocks["006208"].getDividendDatabaseTotalCash(date)
        #     )
        # )
        # nextDividendDay = stock6208.getNextDividendDay(date)
        # nextDividendDay = stocks["006208"].getNextDividendDay(date)

    # end_time = time.time()
    # print("Excution time：", end_time - start_time, " sec")
