import pandas as pd
from src.strategies.base_strategy import BaseStrategy

class ExampleStrategy(BaseStrategy):
    def __init__(self, price: pd.Series, fast_window: int = 10, slow_window: int = 20, direction: str = "long"):
        self.fast_window = fast_window
        self.slow_window = slow_window
        super().__init__(price, direction)

    def generate_signals(self):
        fast_ma = self.price.rolling(self.fast_window).mean()
        slow_ma = self.price.rolling(self.slow_window).mean()

        if self.direction == "long":
            self.long_entry = (fast_ma > slow_ma)
            self.long_exit = (fast_ma < slow_ma)

        elif self.direction == "both":
            self.long_entry = (fast_ma > slow_ma)
            self.long_exit = (fast_ma < slow_ma)
            self.short_entry = (fast_ma < slow_ma)
            self.short_exit = (fast_ma > slow_ma)
