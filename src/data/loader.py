import pandas as pd
import yfinance as yf
import os

def load_price_data(symbol: str, start: str = None, end: str = None, source: str = "yahoo", filepath: str = None) -> pd.DataFrame:

    if source == "yahoo":
        df = yf.download(symbol, start=start, end=end)
        df = df.dropna()
    elif source == "csv":
        if filepath is None or not os.path.exists(filepath):
            raise ValueError("CSV 소스를 사용할 경우 유효한 filepath가 필요합니다.")
        df = pd.read_csv(filepath, parse_dates=True, index_col=0)
        df = df.dropna()
    else:
        raise ValueError(f"지원되지 않는 데이터 소스: {source}")

    df = df.loc[:, ["Open", "High", "Low", "Close", "Volume"]]
    df.index = pd.to_datetime(df.index)
    return df
