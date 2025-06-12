from utils.logger import setup_logger
from data.loader import load_price_data
from strategies.macd_strategy import MACDStrategy

logger = setup_logger()

def main():
    logger.info("🔧 시스템 실행 시작")

    try:
        df = load_price_data("AAPL", start="2024-01-01", end="2024-06-01")
        logger.info(f"📈 데이터 로딩 완료: {df.shape[0]} rows")

        strategy = MACDStrategy(df)
        entries, exits = strategy.get_signals()
        logger.info("✅ 신호 생성 완료")
        logger.debug(f"매수 신호 수: {entries.sum()}, 매도 신호 수: {exits.sum()}")

    except Exception as e:
        logger.exception(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    main()
