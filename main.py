import pandas as pd
import concurrent.futures

from tabulate import tabulate
from colorama import Fore, Style
from backtest import Backtest

# START_DATE = "1960-4-15"
# END_DATE = "2026-11-20"

START_DATE = "2012-12-15"
END_DATE = "2026-01-20"

# START_DATE = "2022-4-15"
# END_DATE = "2026-11-20"

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

# MONTHLY_INVESTMENT = 36000
# COUNTRY = "us"
# STOCK_ID = "TQQQ"

MONTHLY_INVESTMENT = 36000
COUNTRY = "us"
STOCK_ID = "AAPL"

def printResult(results):
    # Convert data to DataFrame
    df = pd.DataFrame(results, columns=['Stock', 'ROI (%)', 'IRR (%)', 'Asset (NTD)', 'Profit (NTD)', 'Dividends (NTD)', 'Costs (NTD)', 'Tax (NTD)'])
    df.to_csv("result.csv",index=False)

    # Define the colorize function
    def colorize(val, max_val, min_val):
        formatted_val = f"{val:,}"
        if val == max_val:
            return f"{Fore.RED}{formatted_val}{Style.RESET_ALL}"
        elif val == min_val:
            return f"{Fore.GREEN}{formatted_val}{Style.RESET_ALL}"
        return formatted_val

    # Apply the colorize function to each column except 'Stock'
    for col in df.columns[1:]:
        max_val = df[col].max()
        min_val = df[col].min()
        df[col] = df[col].apply(colorize, args=(max_val, min_val))

    # Print the table using tabulate
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

def genPrice(dealer):
    plotName = "Price"
    plotList = ["close", "5MA", "20MA", "60MA", "240MA"]
    fig, ax = dealer.genFig(STOCK_ID, plotList, plotName)
    return fig, ax

def genBacktest(country, stock_id, start_date, end_date):
    backtest = Backtest(token, start_date, end_date, commissionCash=1)
    backtest.add(country, stock_id)
    backtest.run()
    result = backtest.printResult()
    return result

def genBacktestPlot(country, stock_id, start_date, end_date):
    plotPriceList = ("Price", ["close"])
    plotDailyList = ("Daily", ["DailyAsset", "DailyCost"])
    plotBiosList = ("BIOS", ["5BIOS", "20BIOS", "60BIOS", "240BIOS"])
    plotRoiList = ("ROI", ["ROI"])
    plotIrrList = ("IRR", ["IRR"])

    backtest = Backtest(token, start_date, end_date, commissionCash=1)
    backtest.add(country, stock_id)

    backtest.run()

    backtest.addTab("Price", plotPriceList)
    backtest.addTab("Accumulated Asset", plotPriceList, plotDailyList)
    backtest.addTab("BIOS", plotPriceList, plotBiosList)
    backtest.addTab("ROI", plotPriceList, plotRoiList)
    backtest.addTab("IRR", plotPriceList, plotIrrList)

    backtest.printResult()
    backtest.show()

if __name__ == "__main__":
    try:
        with open("token.txt", "r") as file:
            token = file.read()

    except FileNotFoundError:
        print("Error: token.txt not found.")
        exit()

    # Create a list of tasks, each task containing the function and its parameters
    tasks = [
        ("us", "QQQ", START_DATE, END_DATE),
        ("us", "^GSPC", START_DATE, END_DATE),
        ("us", "^DJI", START_DATE, END_DATE),
        ("us", "TQQQ", START_DATE, END_DATE),
        ("us", "AAPL", START_DATE, END_DATE),
        ("us", "TSLA", START_DATE, END_DATE),
        ("us", "BAC", START_DATE, END_DATE),
        ("tw", "0050", START_DATE, END_DATE),
        ("tw", "006208", START_DATE, END_DATE)
    ]

    results = []
    # Use ThreadPoolExecutor to manage the thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks to the thread pool
        futures = [executor.submit(genBacktest, country, stock_id, start_date, end_date) for country, stock_id, start_date, end_date in tasks]

        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'Task generated an exception: {exc}')

    print("All threads have completed")
    print(results)
    printResult(results)
