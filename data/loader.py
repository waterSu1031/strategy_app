import pandas as pd
import yfinance as yf
import os

def load_price_data(symbol: str, start: str = None, end: str = None, source: str = "yahoo", filepath: str = None) -> pd.DataFrame:
    """
    가격 데이터를 로드
    :param symbol: 종목 코드 (예: 'AAPL')
    :param start: 시작일자 (예: '2024-01-01')
    :param end: 종료일자 (예: '2024-06-01')
    :param source: 'yahoo' 또는 'csv'
    :param filepath: CSV 로딩 시 경로
    :return: OHLCV 데이터프레임 (datetime 인덱스)
    """
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
