import pandas as pd
from src.data.loader import load_price_data



class FeedSource:

    def __init__(self, symbol: str, start: str, end: str, source: str = "yahoo", filepath: str = None):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.source = source
        self.filepath = filepath
        self.data = None
        self.current_index = 0

    def load(self):
        self.data = load_price_data(
            symbol=self.symbol,
            start=self.start,
            end=self.end,
            source=self.source,
            filepath=self.filepath
        )
        self.current_index = 0

    def has_next(self) -> bool:
        return self.current_index < len(self.data)

    def next(self) -> pd.Series:
        if not self.has_next():
            raise StopIteration("데이터 끝에 도달했습니다.")
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        return row

    def reset(self):
        self.current_index = 0
