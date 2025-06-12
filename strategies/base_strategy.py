import pandas as pd
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    모든 전략 클래스가 상속해야 하는 추상 기본 클래스
    """

    def __init__(self, ohlcv: pd.DataFrame):
        """
        ohlcv: OHLCV DataFrame (인덱스는 datetime)
        """
        self.ohlcv = ohlcv
        self.entries = None
        self.exits = None

    @abstractmethod
    def generate_signals(self):
        """
        전략에 따라 entries, exits를 생성
        반드시 오버라이딩 해야 함
        """
        pass

    def get_signals(self):
        """
        generate_signals 이후 진입/청산 시그널 반환
        """
        if self.entries is None or self.exits is None:
            self.generate_signals()
        return self.entries, self.exits

    def __repr__(self):
        return f"{self.__class__.__name__}(bars={len(self.ohlcv)})"
