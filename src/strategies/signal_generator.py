import vectorbtpro as vbt
import pandas as pd

class SignalGenerator:

    def __init__(self, strategy):
        self.strategy = strategy
        self.price = strategy.price

    def run_backtest(self, **kwargs):
        """
        백테스트용 포트폴리오 실행
        """
        entries, exits, direction = self.strategy.get_signals()
        return vbt.Portfolio.from_signals(
            close=self.price,
            entries=entries,
            exits=exits,
            direction=direction,
            **kwargs
        )

    def initialize_live(self, **kwargs):
        """
        실시간 초기화: 마지막 1봉만 추출해서 LivePortfolio 시작
        """
        entries, exits, direction = self.strategy.get_signals()
        return vbt.LivePortfolio.from_signals_auto(
            close=self.price.iloc[-1:],
            entries=entries.iloc[-1:],
            exits=exits.iloc[-1:],
            direction=direction,
            **kwargs
        )

    def update_live(self, live_pf, new_price: pd.Series):
        """
        새로운 실시간 봉을 기반으로 LivePortfolio 갱신
        """
        # self.strategy.update_price(new_price)
        # self.strategy.generate_signals()
        entries, exits, _ = self.strategy.get_signals()

        live_pf.append(
            new_close=new_price,
            new_entries=entries.iloc[-1:],
            new_exits=exits.iloc[-1:]
        )
