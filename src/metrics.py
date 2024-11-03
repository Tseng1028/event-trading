import numpy as np

class MetricsCalculator:
    def __init__(self, trades):
        self.trades = trades

    def calculate_pnl(self):
        # Implement logic to calculate cumulative PnL
        pass

    def calculate_sharpe_ratio(self):
        # Calculate Sharpe ratio
        pass

    def calculate_cagr(self):
        # Calculate CAGR
        pass

    def calculate_mdd(self):
        # Calculate maximum drawdown
        pass

    def calculate_all_metrics(self):
        return {
            "PnL": self.calculate_pnl(),
            "Sharpe Ratio": self.calculate_sharpe_ratio(),
            "CAGR": self.calculate_cagr(),
            "MDD": self.calculate_mdd()
        }

