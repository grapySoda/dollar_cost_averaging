from stock_database import StockDatabase
import datetime
import os

try:
    with open("token.txt", "r") as file:
        token = file.read()

except FileNotFoundError:
    print("Error: token.txt not found.")
    exit()

stockDb = StockDatabase("006208", token)
