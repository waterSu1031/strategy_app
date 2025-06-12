import pandas as pd
import vectorbtpro as vbt
from strategies.base_strategy import BaseStrategy

class ExampleStrategy(BaseStrategy):
    """
    RSI < 30 이고, 가격이 SMA 아래 → 매수
    RSI > 70 이고, 가격이 SMA 위 → 매도
    """

    def __init__(self, ohlcv: pd.DataFrame, rsi_window: int = 14, sma_window: int = 20):
        super().__init__(ohlcv)
        self.rsi_window = rsi_window
        self.sma_window = sma_window

    def generate_signals(self):
        close = self.ohlcv['Close']

        # 인디케이터 계산
        rsi = vbt.RSI.run(close, window=self.rsi_window).rsi
        sma = vbt.MA.run(close, window=self.sma_window).ma

        # 진입/청산 조건
        entries = (rsi < 30) & (close < sma)
        exits = (rsi > 70) & (close > sma)

        # Boolean 시리즈 저장
        self.entries = entries
        self.exits = exits

    def simulate(self, init_cash: float = 100_000):
        """
        벡테스트용 포트폴리오 시뮬레이션
        """
        pf = vbt.Portfolio.from_signals(
            close=self.ohlcv['Close'],
            entries=self.entries,
            exits=self.exits,
            init_cash=init_cash,
            direction='both'
        )
        return pf
