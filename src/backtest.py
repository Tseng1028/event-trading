import pandas as pd
from .metrics import MetricsCalculator

class EventBacktester:
    def __init__(self, events_df, prices_df):
        self.events_df = events_df
        self.prices_df = prices_df
        self.trades = []

    def execute_trade(self, date, stock_code, action, amount):
        trade = {
            "date": date,
            "stock_code": stock_code,
            "action": action,
            "amount": amount
        }
        self.trades.append(trade)

    def run_backtest(self):
        # Example logic: Iterate over events and execute trades
        for index, row in self.events_df.iterrows():
            self.execute_trade(row['date'], row['stock_code'], row['action'], row['amount'])

    def calculate_metrics(self):
        calculator = MetricsCalculator(self.trades)
        return calculator.calculate_all_metrics()

