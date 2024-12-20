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


def process_taiex_data(df):
    # 確保 datetime 欄位存在並轉換為 datetime 格式
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
    
    # 只保留收盤價欄位，轉換為 Series
    closing_price_series = df['指數收盤價']
    return closing_price_series
