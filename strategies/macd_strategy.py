import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """
    MACD 골든크로스 전략
    - MACD > Signal → 매수
    - MACD < Signal → 매도
    """

    def __init__(self, ohlcv: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__(ohlcv)
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def generate_signals(self):
        close = self.ohlcv['Close']

        # MACD 계산
        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # 시그널 생성
        entries = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        exits = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))

        # 시그널을 Boolean 시리즈로 저장
        self.entries = entries.astype(bool)
        self.exits = exits.astype(bool)

    def __repr__(self):
        return f"MACDStrategy(fast={self.fast}, slow={self.slow}, signal={self.signal_period})"

