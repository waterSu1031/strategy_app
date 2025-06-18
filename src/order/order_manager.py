from typing import Optional, Dict
from order_execution.broker_interface import BrokerInterface
import logging

logger = logging.getLogger("OrderManager")

class OrderManager:
    """
    전략 시그널을 받아 현재 포지션을 고려해 주문을 생성하고,
    브로커를 통해 주문을 실행하는 관리자 클래스
    """

    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.symbol_positions: Dict[str, float] = {}

    def handle_signal(self, symbol: str, signal: str, quantity: float,
                      order_type: str = "market", price: Optional[float] = None,
                      tag: Optional[str] = None):
        """
        시그널에 따라 포지션 상황을 판단하고 주문을 실행
        """
        current_pos = self.get_position_size(symbol)

        if signal == "buy":
            if current_pos > 0:
                logger.info(f"[{symbol}] 이미 롱 포지션 보유 → 생략")
                return
            elif current_pos < 0:
                logger.info(f"[{symbol}] 숏 청산 후 롱 진입")
                self._send_order(symbol, "buy", abs(current_pos) + quantity, order_type, price, tag)
            else:
                logger.info(f"[{symbol}] 신규 롱 진입")
                self._send_order(symbol, "buy", quantity, order_type, price, tag)

        elif signal == "sell":
            if current_pos < 0:
                logger.info(f"[{symbol}] 이미 숏 포지션 보유 → 생략")
                return
            elif current_pos > 0:
                logger.info(f"[{symbol}] 롱 청산 후 숏 진입")
                self._send_order(symbol, "sell", abs(current_pos) + quantity, order_type, price, tag)
            else:
                logger.info(f"[{symbol}] 신규 숏 진입")
                self._send_order(symbol, "sell", quantity, order_type, price, tag)

    def _send_order(self, symbol: str, side: str, quantity: float,
                    order_type: str, price: Optional[float], tag: Optional[str]):
        order = self.broker.send_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            tag=tag
        )

        if order.get("status") == "filled":
            logger.info(f"[{symbol}] 주문 체결 완료: {order}")
        elif order.get("status") == "submitted":
            logger.info(f"[{symbol}] 주문 제출됨: {order}")
        else:
            logger.warning(f"[{symbol}] 주문 실패 또는 거절: {order}")

        self._update_position(symbol)

    def get_position_size(self, symbol: str) -> float:
        pos = self.broker.get_position(symbol)
        return pos.get("size", 0.0)

    def _update_position(self, symbol: str):
        pos = self.broker.get_position(symbol)
        self.symbol_positions[symbol] = pos.get("size", 0.0)

    def refresh_all_positions(self):
        positions = self.broker.get_all_positions()
        for symbol, info in positions.items():
            self.symbol_positions[symbol] = info.get("size", 0.0)

    def close_all_positions(self):
        for symbol, size in self.symbol_positions.items():
            if size > 0:
                self._send_order(symbol, "sell", size, order_type="market", price=None, tag="close_all")
            elif size < 0:
                self._send_order(symbol, "buy", abs(size), order_type="market", price=None, tag="close_all")
