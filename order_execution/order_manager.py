from typing import Optional, Dict
from order_execution.broker_interface import BrokerInterface
import logging

logger = logging.getLogger("OrderManager")

class OrderManager:
    """
    전략에서 생성된 시그널을 받아,
    현재 포지션 상태를 고려하여 주문 실행 여부를 판단하고 브로커에 전달
    """

    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.symbol_positions: Dict[str, float] = {}  # 예: {'AAPL': 100.0}

    def handle_signal(self, symbol: str, signal: str, quantity: float,
                      order_type: str = "market", price: Optional[float] = None,
                      tag: Optional[str] = None):
        """
        매수/매도 신호를 받아 주문 여부를 판단하고 브로커로 전달
        """
        current_pos = self.get_position_size(symbol)

        if signal == "buy":
            if current_pos > 0:
                logger.info(f"[{symbol}] 이미 매수 포지션 보유 중 → 주문 생략")
                return
            elif current_pos < 0:
                logger.info(f"[{symbol}] 숏 포지션 청산 후 롱 진입")
                self._send_order(symbol, "buy", quantity * 2, order_type, price, tag)
            else:
                logger.info(f"[{symbol}] 신규 매수 진입")
                self._send_order(symbol, "buy", quantity, order_type, price, tag)

        elif signal == "sell":
            if current_pos < 0:
                logger.info(f"[{symbol}] 이미 숏 포지션 보유 중 → 주문 생략")
                return
            elif current_pos > 0:
                logger.info(f"[{symbol}] 롱 포지션 청산 후 숏 진입")
                self._send_order(symbol, "sell", quantity * 2, order_type, price, tag)
            else:
                logger.info(f"[{symbol}] 신규 매도 진입")
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
            logger.info(f"[{symbol}] 주문 체결: {order}")
            self._update_position(symbol)
        else:
            logger.warning(f"[{symbol}] 주문 실패 or 거절: {order}")

    def get_position_size(self, symbol: str) -> float:
        pos = self.broker.get_position(symbol)
        return pos.get("size", 0.0)

    def _update_position(self, symbol: str):
        pos = self.broker.get_position(symbol)
        self.symbol_positions[symbol] = pos.get("size", 0.0)
