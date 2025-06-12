import abc
from typing import Optional, Dict

class BrokerInterface(abc.ABC):
    """
    실거래 또는 백테스트를 위한 브로커 인터페이스 추상 클래스
    """

    @abc.abstractmethod
    def send_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "market", price: Optional[float] = None,
                   tag: Optional[str] = None) -> Dict:
        """
        주문 전송
        :param symbol: 종목 코드 (예: 'AAPL')
        :param side: 'buy' or 'sell'
        :param quantity: 수량
        :param order_type: 'market', 'limit' 등
        :param price: 지정가 주문일 경우 가격
        :param tag: 전략 식별 태그 등
        :return: 체결 정보 또는 주문 ID
        """
        pass

    @abc.abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        미체결 주문 취소
        :param order_id: 주문 식별자
        :return: 취소 성공 여부
        """
        pass

    @abc.abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        현재 열린(미체결) 주문 리스트 반환
        """
        pass

    @abc.abstractmethod
    def get_position(self, symbol: str) -> Dict:
        """
        현재 포지션 상태 조회
        :return: {"symbol": "AAPL", "size": 10, "avg_price": 181.5}
        """
        pass

    @abc.abstractmethod
    def get_account_info(self) -> Dict:
        """
        잔고, 자산, 현금 등의 계좌 정보
        """
        pass
