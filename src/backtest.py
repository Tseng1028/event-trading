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
        # 定義一個處理每筆交易訊號的函數
        def process_signals(signals, date):
            for stock_code, action in signals.items():
                if pd.notna(action):
                    price = self.get_price(date, stock_code)
                    
                    # 確保 price 不是 None 再進行操作
                    if price is None:
                        continue

                    # 檢查持倉，確保有持倉才能賣出
                    if action == 'sell' and self.position.get(stock_code, {}).get("amount", 0) == 0:
                        continue

                    trade_amount = 1  # 假設每次交易的數量為 1
                    fee = trade_amount * price * self.fee_rate  # 計算手續費
                    pnl = self.calculate_trade_pnl(action, trade_amount, price, stock_code) - fee  # 扣除手續費

                    # 記錄交易
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

        # 使用 apply 來遍歷每一行，並傳遞日期作為參數
        self.events_df.apply(lambda row: process_signals(row, row.name), axis=1)

    def get_price(self, date, stock_code):
        # 從 prices_df 中獲取指定日期和股票的收盤價
        if stock_code in self.prices_df.columns:
            return self.prices_df.loc[date, stock_code]
        return None

    def calculate_trade_pnl(self, action, amount, price, stock_code):
        # 若為買入操作，僅更新持倉成本，不計算損益
        if action == 'buy':
            # 若已持有股票，使用加權平均法更新買入價格
            if stock_code in self.position:
                total_amount = self.position[stock_code]["amount"] + amount
                average_price = (
                    self.position[stock_code]["price"] * self.position[stock_code]["amount"] + price * amount
                ) / total_amount
                self.position[stock_code] = {"price": average_price, "amount": total_amount}
            else:
                # 若無持倉，直接記錄該股票的買入價格和數量
                self.position[stock_code] = {"price": price, "amount": amount}
            return 0  # 買入時不計算損益

        elif action == 'sell':
            # 若為賣出操作，計算損益
            if stock_code in self.position and self.position[stock_code]["amount"] >= amount:
                buy_price = self.position[stock_code]["price"]  # 取出買入價格
                pnl = (price - buy_price) * amount  # (賣出價格 - 買入價格) * 賣出數量
                # 更新持倉數量
                self.position[stock_code]["amount"] -= amount
                # 若持倉量為 0，刪除該股票的持倉資訊
                if self.position[stock_code]["amount"] == 0:
                    del self.position[stock_code]
                return pnl
            else:
                raise ValueError(f"持倉不足，無法賣出股票 {stock_code}")
        return 0

    def update_position(self, action, stock_code, amount, price):
        # 更新持倉和累計損益
        if action == 'buy':
            if stock_code in self.position:
                self.position[stock_code]["amount"] += amount
            else:
                self.position[stock_code] = {"price": price, "amount": amount}
        elif action == 'sell' and stock_code in self.position:
            if self.position[stock_code]["amount"] >= amount:
                self.pnl += (price - self.position[stock_code]["price"]) * amount
                self.position[stock_code]["amount"] -= amount
                if self.position[stock_code]["amount"] == 0:
                    del self.position[stock_code]  # 移除持倉為 0 的股票

    def calculate_metrics(self):
        # 計算績效指標
        metrics_calculator = MetricsCalculator(pd.DataFrame(self.trades))
        return metrics_calculator.calculate_all_metrics()

    def get_trades_df(self):
        """將交易記錄轉換為 DataFrame"""
        return pd.DataFrame(self.trades)
