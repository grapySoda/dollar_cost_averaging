from FinMind.data import DataLoader
import datetime
import os

try:
    with open("token.txt", "r") as file:
        token = file.read()

except FileNotFoundError:
    print("Error: token.txt not found.")
    exit()

stock_id = "006208"

start_date = datetime.date(1960, 4, 15)
end_date = datetime.date.today()

api = DataLoader()
api.login_by_token(api_token=token)

path = "taiwan_stock_dividend"
df = api.taiwan_stock_dividend(
    stock_id=stock_id,
    start_date=start_date,
)

df["TotalStock"] = df["StockEarningsDistribution"] + df["StockStatutorySurplus"]
df["TotalCash"] = df["CashEarningsDistribution"] + df["CashStatutorySurplus"]
df = df[["date", "stock_id", "CashDividendPaymentDate", "TotalStock", "TotalCash"]]

if not os.path.exists(path):
    os.makedirs(path)
df.to_csv("{}/{}.csv".format("taiwan_stock_dividend", stock_id), index=False)

print(df)
print(type(df))
