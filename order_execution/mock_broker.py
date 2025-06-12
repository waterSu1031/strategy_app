from typing import Dict, List, Optional
from order_execution.broker_interface import BrokerInterface
import uuid
import time

class MockBroker(BrokerInterface):
    """
    백테스트 또는 테스트용 가짜 브로커
    실제 주문은 발생하지 않지만, 주문을 기록하고 체결된 것처럼 동작
    """

    def __init__(self, initial_cash: float = 1_000_000):
        self.cash = initial_cash
        self.positions: Dict[str, Dict] = {}  # {symbol: {'size': float, 'avg_price': float}}
        self.orders: Dict[str, Dict] = {}     # {order_id: {...}}

    def send_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "market", price: Optional[float] = None,
                   tag: Optional[str] = None) -> Dict:
        order_id = str(uuid.uuid4())
        timestamp = time.time()

        # 체결된 것처럼 즉시 반영
        fill_price = price if price else 100.0  # 실제 가격정보 없으면 임의 가격
        cost = quantity * fill_price

        if side == "buy":
            if self.cash >= cost:
                self.cash -= cost
                self._update_position(symbol, quantity, fill_price)
            else:
                return {"status": "rejected", "reason": "Insufficient cash"}
        elif side == "sell":
            pos = self.positions.get(symbol, {'size': 0})
            if pos['size'] >= quantity:
                self.cash += cost
                self._update_position(symbol, -quantity, fill_price)
            else:
                return {"status": "rejected", "reason": "Insufficient holdings"}

        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": fill_price,
            "timestamp": timestamp,
            "status": "filled",
            "tag": tag
        }

        self.orders[order_id] = order
        return order

    def cancel_order(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if order and order["status"] == "open":
            order["status"] = "cancelled"
            return True
        return False

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        orders = [
            o for o in self.orders.values()
            if o["status"] == "open" and (symbol is None or o["symbol"] == symbol)
        ]
        return orders

    def get_position(self, symbol: str) -> Dict:
        return self.positions.get(symbol, {"symbol": symbol, "size": 0.0, "avg_price": 0.0})

    def get_account_info(self) -> Dict:
        return {
            "cash": self.cash,
            "positions": self.positions,
            "total_equity": self._calculate_total_equity()
        }

    def _update_position(self, symbol: str, quantity: float, price: float):
        pos = self.positions.get(symbol)
        if pos:
            total_qty = pos['size'] + quantity
            if total_qty == 0:
                self.positions.pop(symbol)
                return
            avg_price = (
                (pos['size'] * pos['avg_price']) + (quantity * price)
            ) / total_qty
            self.positions[symbol] = {'size': total_qty, 'avg_price': avg_price}
        else:
            self.positions[symbol] = {'size': quantity, 'avg_price': price}

    def _calculate_total_equity(self) -> float:
        unrealized = sum(p['size'] * p['avg_price'] for p in self.positions.values())
        return self.cash + unrealized
