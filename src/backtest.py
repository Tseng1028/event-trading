import pandas as pd
from .metrics import MetricsCalculator

class EventBacktester:
    def __init__(self, events_df, prices_df, trade_conditions, fee_rate=0.001425*0.6):
        """
        :param events_df: 包含事件訊號的 DataFrame
        :param prices_df: 包含收盤價的 DataFrame
        :param trade_conditions: 用來設定交易條件的函數
        :param fee_rate: 手續費率，默認為0.001425*0.6
        """
        self.events_df = events_df
        self.prices_df = prices_df
        self.trade_conditions = trade_conditions
        self.fee_rate = fee_rate  # 手續費率
        self.trades = []
        self.position = {}
        self.pnl = 0

    def apply_trade_conditions(self):
        # 根據 trade_conditions 函數設置買賣條件
        self.events_df = self.events_df.apply(self.trade_conditions)

    def execute_trades(self):
        # 根據 events_df 的交易訊號執行交易
        for date, signals in self.events_df.iterrows():
            for stock_code, action in signals.items():
                if pd.notna(action):
                    price = self.get_price(date, stock_code)
                    if price is not None:
                        if action == 'sell' and self.position.get(stock_code, 0) == 0:
                            # 當無持倉且有賣出訊號時跳過該筆交易
                            continue
                        
                        trade_amount = 1  # 假設每次交易的數量為 1
                        fee = trade_amount * price * self.fee_rate  # 計算手續費
                        pnl = self.calculate_trade_pnl(action, trade_amount, price) - fee  # 扣除手續費

                        trade = {
                            "date": date,
                            "stock_code": stock_code,
                            "action": action,
                            "amount": trade_amount,
                            "price": price,
                            "fee": fee,
                            "pnl": pnl
                        }
                        self.trades.append(trade)
                        self.update_position(action, stock_code, trade_amount, price)

    def get_price(self, date, stock_code):
        # 從 prices_df 中獲取指定日期和股票的收盤價
        if stock_code in self.prices_df.columns:
            return self.prices_df.loc[date, stock_code]
        return None

    def calculate_trade_pnl(self, action, amount, price):
        # 計算交易的損益（不含手續費）
        if action == 'buy':
            return -amount * price
        elif action == 'sell':
            return amount * price
        return 0

    def update_position(self, action, stock_code, amount, price):
        # 更新持倉和累計損益
        if action == 'buy':
            self.position[stock_code] = self.position.get(stock_code, 0) + amount
        elif action == 'sell' and stock_code in self.position and self.position[stock_code] >= amount:
            # 確保只有在持倉數量足夠時才執行賣出操作
            self.pnl += amount * price
            self.position[stock_code] -= amount
            if self.position[stock_code] == 0:
                del self.position[stock_code]  # 移除持倉為 0 的股票

    def calculate_metrics(self):
        # 計算績效指標
        metrics_calculator = MetricsCalculator(pd.DataFrame(self.trades))
        return metrics_calculator.calculate_all_metrics()
