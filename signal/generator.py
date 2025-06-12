import pandas as pd

class SignalGenerator:
    """
    시그널 시리즈에서 특정 시점의 진입/청산 신호를 추출하는 유틸 클래스
    """

    def __init__(self):
        pass  # 향후 필터 조건 추가 가능

    def extract_point(self, timestamp, entries: pd.Series, exits: pd.Series) -> (bool, bool):
        """
        주어진 timestamp에서 진입/청산 시그널이 존재하는지 반환

        :param timestamp: 현재 시점 (datetime index)
        :param entries: 매수 조건 Boolean Series
        :param exits: 매도 조건 Boolean Series
        :return: (is_entry, is_exit)
        """
        entry = False
        exit = False

        if timestamp in entries.index:
            entry = bool(entries.loc[timestamp])
        if timestamp in exits.index:
            exit = bool(exits.loc[timestamp])

        return entry, exit
