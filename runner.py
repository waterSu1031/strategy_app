from src.strategies.example import ExampleStrategy
from src.strategies.signal import PortfolioRunner
from src.data import load_ibkr_data, stream_ibkr_data


def run(mode="backtest", symbol="AAPL", bar_size="5min", lookback="2h"):
    assert mode in ["backtest", "live"], "mode는 'backtest' 또는 'live'만 가능합니다"

    # 1. 초기 데이터 로드
    price = load_ibkr_data(symbol=symbol, size=bar_size, lookback=lookback)["Close"]

    # 2. 전략 인스턴스화
    strategy = ExampleStrategy(price, direction="both")
    strategy.run()

    # 3. 백테스트 실행
    runner = PortfolioRunner(strategy)
    if mode == "backtest":
        # runner = PortfolioRunner(strategy)
        back_pf = runner.run_backtest()
        print(back_pf.stats())
        # return pf

    # 4. 실시간 실행
    elif mode == "live":

        live_pf = runner.initialize_live()

        print("[LIVE MODE] 실시간 데이터 수신 시작...")

        # 실시간 봉 수신 루프
        for new_bar in stream_ibkr_data(symbol=symbol, size=bar_size):
            if new_bar is None:
                continue

            # 포맷: pd.Series([가격], index=[Timestamp])
            strategy.update_price(new_bar)
            # entry, exit, _ = strategy.generate_signals()
            entry, exit, _ = strategy.get_signals()
            #
            runner.update_live(live_pf, new_bar)

            # 마지막 포지션 출력 예시
            print("현재 포지션:", live_pf.position.iloc[-1])

        # return live_pf

#
#
# # 1. 다운로드 데이터
# price = load_price("AAPL", size="5min", lookback="3h")["Close"]
#
# # 2. 전략 객체 생성 및 실행
# strategy = ExampleStrategy(price, direction="both")
# strategy.run()  # → generate_signals() 실행
#
# # 3. 시그널 추출
# entry, exit, direction = strategy.get_signals()
#
# # 4. 포트폴리오 백테스트 실행
# pf = vbt.Portfolio.from_signals(
#     close=price,
#     entries=entry,
#     exits=exit,
#     direction=direction
# )
# print(pf.stats())
#
#
#
# # 3. 실시간 수신 데이터 (예: 새로운 5분봉)
# from datetime import datetime
# new_bar = pd.Series([123.45], index=[pd.Timestamp(datetime.now())])
#
# # 4. 전략에 가격 업데이트
# strategy.update_price(new_bar)
#
# # 5. 실시간 신호 재생성
# strategy.generate_signals()
#
# # 6. 마지막 시그널 추출
# entry, exit, direction = strategy.get_signals()
# entry_last = entry.iloc[-1]
# exit_last = exit.iloc[-1]
#
# # 7. 실시간 포트폴리오 갱신 예시
# from vectorbt.portfolio.enums import SizeType
# live_pf.append(
#     new_close=new_bar,
#     new_entries=pd.Series([entry_last], index=new_bar.index),
#     new_exits=pd.Series([exit_last], index=new_bar.index),
#     size_type=SizeType.Target  # 또는 원하는 사이즈 타입
# )