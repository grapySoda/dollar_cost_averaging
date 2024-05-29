from datetime import datetime
from collections import deque
import pandas as pd
import copy


class Transaction:
    def __init__(self, stock, date, price, quantity, cost, action, roi=0):
        self.stock = stock
        self.date = datetime.strptime(date, "%Y/%m/%d")
        self.price = price
        self.quantity = quantity
        self.cost = cost
        self.action = action
        self.roi = roi

    def __repr__(self):
        return f"Transaction(date={self.date.strftime('%Y/%m/%d')}, price={self.price}, quantity={self.quantity}, cost={self.cost})"


class Stock:
    def __init__(self):
        self.quantities = 0
        self.pnl = 0
        self.cost = 0
        self.hold = []
        self.buyTransactions = []
        self.sellTransactions = []

    def __repr__(self):
        return f"Stock(buyTransactions={self.buyTransactions})"


class Dealer:
    def __init__(self):
        self._stocks = {}
        self.pnl = 0
        self.cost = 0
        self.currentPnl = 0

    def buy(self, date, stock, quantity, price):
        print("Buy: {},\tprice: {},\tshares: {}".format(stock, price, quantity))
        if stock not in self._stocks:
            self._stocks[stock] = Stock()
        cost = quantity * price
        transaction = Transaction(stock, date, price, quantity, cost, "buy")
        self._stocks[stock].buyTransactions.append(transaction)
        self._stocks[stock].hold.append(copy.deepcopy(transaction))
        self._stocks[stock].quantities += quantity
        self._stocks[stock].cost += cost
        self.cost += cost

    def sell(self, date, stock, quantity, price):
        if quantity > self._stocks[stock].quantities:
            print(
                "Quantities out of range, current: {}, sell: {}".format(
                    self._stocks[stock].quantities, quantity
                )
            )
            return

        self.currentPnl = 0
        self.currentCost = 0
        print("Sell: {},\tprice: {},\tshares: {}".format(stock, price, quantity))
        cost = 0
        self.recursiveSell(stock, price, quantity)
        roi = int(self.currentPnl / self.currentCost * 100)
        print("self.currentPnl", self.currentPnl)
        print("self.currentCost", self.currentCost)
        transaction = Transaction(stock, date, price, quantity, cost, "sell", roi)
        self._stocks[stock].sellTransactions.append(transaction)

    def recursiveSell(self, stock, price, quantity):
        if self._stocks[stock].hold[0].quantity > quantity:
            self._stocks[stock].hold[0].quantity -= quantity
            pnl = int((price - self._stocks[stock].hold[0].price) * quantity)
            self.pnl += pnl
            self.currentPnl += pnl
            self.currentCost += self._stocks[stock].hold[0].price * quantity
            self._stocks[stock].pnl += pnl
            self._stocks[stock].quantities -= quantity

        elif self._stocks[stock].hold[0].quantity == quantity:
            pnl = int((price - self._stocks[stock].hold[0].price) * quantity)
            self.pnl += pnl
            self.currentPnl += pnl
            self.currentCost += self._stocks[stock].hold[0].price * quantity
            self._stocks[stock].pnl += pnl
            self._stocks[stock].hold.pop(0)
            self._stocks[stock].quantities -= quantity

        else:
            totalQuantity = self._stocks[stock].hold[0].quantity
            quantity -= totalQuantity
            pnl = int((price - self._stocks[stock].hold[0].price) * totalQuantity)
            self.pnl += pnl
            self.currentPnl += pnl
            self.currentCost += self._stocks[stock].hold[0].price * totalQuantity
            self._stocks[stock].pnl += pnl
            self._stocks[stock].hold.pop(0)
            self._stocks[stock].quantities -= totalQuantity
            self.recursiveSell(stock, price, quantity)

    def printTransactionHistory(self):
        list = []
        for id in self._stocks:
            for item in self._stocks[id].buyTransactions:
                list.append(
                    [
                        item.stock,
                        item.date,
                        item.quantity,
                        item.price,
                        item.cost,
                        item.roi,
                        item.action,
                    ]
                )

            for item in self._stocks[id].sellTransactions:
                list.append(
                    [
                        item.stock,
                        item.date,
                        item.quantity,
                        item.price,
                        item.cost,
                        item.roi,
                        item.action,
                    ]
                )

        df = pd.DataFrame(
            list,
            columns=["Stock", "Date", "Quantity", "Price", "Cost", "ROI(%)", "Action"],
        )
        df["ROI(%)"] = df["ROI(%)"].astype(str) + " %"
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date")
        print(df)

    def __repr__(self):
        return f"Dealer(stocks={self._stocks})"


dealer = Dealer()
dealer.buy("2020/01/15", "2330", 20, 20)
# dealer.buy("2020/01/16", "006208", 50, 100)
dealer.buy("2020/01/16", "2330", 40, 40)

# dealer.printAsset()
dealer.sell("2020/01/17", "2330", 21, 20)
# dealer.printAsset()
# dealer.sell("2020/01/18", "2330", 60, 10)
# dealer.printAsset()

dealer.printTransactionHistory()
