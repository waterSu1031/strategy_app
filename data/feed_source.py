import pandas as pd
from data.loader import load_price_data

class FeedSource:
    """
    데이터 피드 소스 클래스
    - 기본적으로는 과거 데이터를 순차적으로 feed
    - 나중에 실시간 스트리밍도 여기로 대체 가능
    """

    def __init__(self, symbol: str, start: str, end: str, source: str = "yahoo", filepath: str = None):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.source = source
        self.filepath = filepath
        self.data = None
        self.current_index = 0

    def load(self):
        """
        데이터를 로딩하고 초기화
        """
        self.data = load_price_data(
            symbol=self.symbol,
            start=self.start,
            end=self.end,
            source=self.source,
            filepath=self.filepath
        )
        self.current_index = 0

    def has_next(self) -> bool:
        """
        다음 데이터가 있는지 여부
        """
        return self.current_index < len(self.data)

    def next(self) -> pd.Series:
        """
        다음 시점의 데이터를 반환
        """
        if not self.has_next():
            raise StopIteration("데이터 끝에 도달했습니다.")
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        return row

    def reset(self):
        self.current_index = 0
