import unittest
from data.loader import load_data
from data.resampler import resample_ohlcv
from strategies.macd_strategy import MACDStrategy

class TestMACDStrategy(unittest.TestCase):
    def test_generate_signals(self):
        df = load_data("AAPL", start="2023-01-01", timeframe="1h")
        df = resample_ohlcv(df, "1h")

        strat = MACDStrategy(df)
        entries, exits = strat.get_signals()

        # 진입/청산 시그널이 bool Series인지 확인
        self.assertTrue(isinstance(entries, df['Close'].__class__))
        self.assertTrue(isinstance(exits, df['Close'].__class__))
        self.assertTrue(entries.dtype == bool)
        self.assertTrue(exits.dtype == bool)

        # 시그널의 길이가 데이터와 일치해야 함
        self.assertEqual(len(entries), len(df))
        self.assertEqual(len(exits), len(df))

if __name__ == "__main__":
    unittest.main()
