import time
from data.feed_source import FeedSource
from strategies.example_strategy import ExampleStrategy
from signal.generator import SignalGenerator
from order_execution.mock_broker import MockBroker
from order_execution.order_manager import OrderManager
from utils.logger import setup_logger

logger = setup_logger("Runner")

class Runner:

    def __init__(self, symbol: str, start: str, end: str, range_size: float = 1.0):
        self.symbol = symbol
        self.feed = FeedSource(symbol, start, end)
        self.broker = MockBroker()
        self.order_manager = OrderManager(self.broker)
        self.range_size = range_size
        self.strategy = None
        self.signal_generator = SignalGenerator()

    def initialize(self):
        logger.info(f"🚀 피드 초기화: {self.symbol}")
        self.feed.load()

        # 전체 데이터를 초기 전략에 주입
        df = self.feed.data.copy()
        self.strategy = ExampleStrategy(df)
        self.strategy.generate_signals()

    def run(self, sleep_time: float = 0.05):

        logger.info("▶ 실행 시작")
        self.initialize()

        while self.feed.has_next():
            bar = self.feed.next()
            timestamp = bar.name

            # 현재 시점에 진입/청산 신호 있는지 확인
            entry, exit = self.signal_generator.extract_point(
                timestamp, self.strategy.entries, self.strategy.exits
            )

            if entry:
                logger.info(f"[{timestamp}] 🟢 매수 시그널 감지")
                self.order_manager.handle_signal(self.symbol, "buy", quantity=10)

            elif exit:
                logger.info(f"[{timestamp}] 🔴 매도 시그널 감지")
                self.order_manager.handle_signal(self.symbol, "sell", quantity=10)

            time.sleep(sleep_time)

        logger.info("🏁 실행 종료")
        account = self.broker.get_account_info()
        logger.info(f"📊 최종 잔고: {account['cash']:.2f}, 포지션: {account['positions']}")
