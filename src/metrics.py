import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class MetricsCalculator:
    def __init__(self, trades_df, taiex_returns=None):
        self.trades_df = trades_df
        self.taiex_returns = taiex_returns if taiex_returns is not None else pd.Series(dtype=float)
        self.trades_df['cumulative_pnl'] = self.trades_df['pnl'].cumsum()

    def calculate_pnl(self):
        return self.trades_df['pnl'].sum()

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        daily_returns = self.trades_df['pnl']
        excess_returns = daily_returns - risk_free_rate
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

    def calculate_cagr(self):
        total_days = (self.trades_df['date'].max() - self.trades_df['date'].min()).days
        final_value = self.trades_df['cumulative_pnl'].iloc[-1]
        return (1 + final_value) ** (365 / total_days) - 1

    def calculate_mdd(self):
        cumulative_pnl = self.trades_df['cumulative_pnl']
        rolling_max = cumulative_pnl.cummax()
        drawdown = (cumulative_pnl - rolling_max) / rolling_max
        return drawdown.min()

    def calculate_all_metrics(self):
        return {
            "PnL": self.calculate_pnl(),
            "Sharpe Ratio": self.calculate_sharpe_ratio(),
            "CAGR": self.calculate_cagr(),
            "MDD": self.calculate_mdd()
        }

    def calculate_cumulative_returns(self):
        # 確保 TAIEX 的累積報酬與策略的累積報酬日期對齊
        if not self.taiex_returns.empty:
            taiex_cumulative = (1 + self.taiex_returns).cumprod() - 1  # 計算 TAIEX 累積報酬
            taiex_cumulative = taiex_cumulative.reindex(self.trades_df['date']).fillna(method='ffill')
        else:
            taiex_cumulative = pd.Series(0, index=self.trades_df['date'])
        
        cumulative_returns = pd.DataFrame({
            "date": self.trades_df["date"],
            "strategy_cumulative": self.trades_df["cumulative_pnl"],
            "taiex_cumulative": taiex_cumulative
        })
        cumulative_returns["excess_return"] = cumulative_returns["strategy_cumulative"] - cumulative_returns["taiex_cumulative"]
        return cumulative_returns

    def plot_cumulative_returns(self, cumulative_returns):
        plt.figure(figsize=(12, 6))
        plt.plot(cumulative_returns["date"], cumulative_returns["strategy_cumulative"], label="Strategy Cumulative Return")
        plt.plot(cumulative_returns["date"], cumulative_returns["taiex_cumulative"], label="TAIEX Future Cumulative Return")
        plt.plot(cumulative_returns["date"], cumulative_returns["excess_return"], label="Excess Return (Strategy - TAIEX)")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Return")
        plt.title("Cumulative Return Comparison")
        plt.legend()
        plt.show()


