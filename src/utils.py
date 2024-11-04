import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path, index_col="datetime", parse_dates=True)

def trade_conditions(row):
    """
    設定交易條件函數，根據自定義的邏輯修改事件訊號。
    例如，值大於 50 的設定為 "buy"，小於 50 的設定為 "sell"，其餘為空值。
    """
    new_row = row.copy()
    for symbol in row.index:
        if pd.notna(row[symbol]):
            if row[symbol] > 50:
                new_row[symbol] = "buy"
            elif row[symbol] < 50:
                new_row[symbol] = "sell"
            else:
                new_row[symbol] = None
    return new_row

