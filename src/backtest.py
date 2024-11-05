import pandas as pd
from .metrics import MetricsCalculator

class EventBacktester:
    def __init__(self, events_df, prices_df, trade_conditions, buy_fee_rate=0.001425*0.6, sell_fee_rate=0.001425*0.6+0.003):
        """
        :param events_df: 包含事件訊號的 DataFrame
        :param prices_df: 包含收盤價的 DataFrame
        :param trade_conditions: 用來設定交易條件的函數
        :param buy_fee_rate: 買入手續費率，默認為0.001425*0.6
        :param sell_fee_rate: 賣出手續費率，默認為0.001425
        """
        self.events_df = events_df
        self.prices_df = prices_df
        self.trade_conditions = trade_conditions
        self.buy_fee_rate = buy_fee_rate  # 買入手續費率
        self.sell_fee_rate = sell_fee_rate  # 賣出手續費率
        self.trades = []
        self.position = {}
        self.pnl = 0

    def apply_trade_conditions(self):
        # 根據 trade_conditions 函數設置買賣條件(此用apply方法逐行產生交易訊號)
        self.events_df = self.events_df.apply(self.trade_conditions)

    def df_trade_conditions(self):
        #輸入輸出都是dataframe
        self.events_df = self.trade_conditions(self.events_df)    

    def execute_trades(self):
        # 定義一個處理每筆交易訊號的函數
        def process_signals(signals, date):
            for stock_code, action in signals.items():
                if pd.notna(action):
                    price = self.get_price(date, stock_code)
                    
                    # 確保 price 不是 None 再進行操作
                    if price is None:
                        continue

                    # 設定 trade_amount 的預設值為 0
                    trade_amount = 0

                    # 檢查持倉，若有持倉且出現賣出訊號，則賣出全部持倉
                    if action == 'sell' and stock_code in self.position:
                        trade_amount = self.position[stock_code]["amount"]
                        fee = trade_amount * price * self.sell_fee_rate  # 計算賣出手續費
                        pnl = self.calculate_trade_pnl(action, trade_amount, price, stock_code) - fee  # 扣除手續費

                    elif action == 'buy':
                        trade_amount = 1  # 假設每次交易的數量為 1
                        fee = trade_amount * price * self.buy_fee_rate  # 計算買入手續費
                        pnl = -fee  # 買入時的 PnL 僅為手續費的支出

                    # 若 trade_amount 為 0，不進行交易
                    if trade_amount == 0:
                        continue

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
        # 僅負責損益計算，不更新持倉
        if action == 'sell' and stock_code in self.position:
            buy_price = self.position[stock_code]["price"]
            pnl = (price - buy_price) * amount  # (賣出價格 - 買入價格) * 賣出數量
            return pnl
        return 0

    def update_position(self, action, stock_code, amount, price):
        # 買入時將手續費計入成本
        if action == 'buy':
            adjusted_price = price * (1 + self.buy_fee_rate)  # 包含手續費的買入成本
            if stock_code in self.position:
                # 使用加權平均法計算新成本
                current_amount = self.position[stock_code]["amount"]
                current_price = self.position[stock_code]["price"]
                total_amount = current_amount + amount
                weighted_price = (current_price * current_amount + adjusted_price * amount) / total_amount
                self.position[stock_code] = {"price": weighted_price, "amount": total_amount}
            else:
                # 沒有持倉則新建
                self.position[stock_code] = {"price": adjusted_price, "amount": amount}
        
        elif action == 'sell' and stock_code in self.position:
            # 減少持倉，不計算手續費
            if self.position[stock_code]["amount"] >= amount:
                self.position[stock_code]["amount"] -= amount
                if self.position[stock_code]["amount"] == 0:
                    del self.position[stock_code]


    def calculate_metrics(self):
        # 計算績效指標
        metrics_calculator = MetricsCalculator(pd.DataFrame(self.trades))
        return metrics_calculator.calculate_all_metrics()

    def get_trades_df(self):
        """將交易記錄轉換為 DataFrame"""
        return pd.DataFrame(self.trades)
