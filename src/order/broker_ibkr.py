# ibkr_broker.py

from ib_insync import IB, Stock, util, Order
from typing import Dict, List, Optional
from order_execution.broker_interface import BrokerInterface
import time

class IBKRBroker(BrokerInterface):
    def __init__(self, host="127.0.0.1", port=7497, client_id=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)

    def _stock_contract(self, symbol: str) -> Stock:
        return Stock(symbol, "SMART", "USD")

    def send_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "market", price: Optional[float] = None,
                   tag: Optional[str] = None) -> Dict:
        contract = self._stock_contract(symbol)
        if order_type == "market":
            order = Order(action=side.upper(), totalQuantity=quantity, orderType="MKT")
        elif order_type == "limit":
            order = Order(action=side.upper(), totalQuantity=quantity,
                          orderType="LMT", lmtPrice=price)
        else:
            raise ValueError(f"지원되지 않는 주문 유형: {order_type}")

        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)  # 체결 대기

        status = trade.orderStatus.status
        fill_price = trade.fills[0].execution.price if trade.fills else None

        return {
            "order_id": trade.order.permId,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": fill_price,
            "status": status,
            "tag": tag
        }

    def cancel_order(self, order_id: str) -> bool:
        for trade in self.ib.trades():
            if str(trade.order.permId) == order_id:
                self.ib.cancelOrder(trade.order)
                return True
        return False

    def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        count = 0
        for trade in self.ib.trades():
            if trade.orderStatus.status == "Submitted":
                if symbol is None or trade.contract.symbol == symbol:
                    self.ib.cancelOrder(trade.order)
                    count += 1
        return count

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        result = []
        for trade in self.ib.trades():
            if trade.orderStatus.status == "Submitted":
                if symbol is None or trade.contract.symbol == symbol:
                    result.append({
                        "order_id": trade.order.permId,
                        "symbol": trade.contract.symbol,
                        "side": trade.order.action.lower(),
                        "quantity": trade.order.totalQuantity,
                        "status": trade.orderStatus.status
                    })
        return result

    def get_order_status(self, order_id: str) -> Dict:
        for trade in self.ib.trades():
            if str(trade.order.permId) == order_id:
                return {
                    "order_id": order_id,
                    "symbol": trade.contract.symbol,
                    "status": trade.orderStatus.status,
                    "filled": trade.orderStatus.filled,
                    "remaining": trade.orderStatus.remaining
                }
        return {"order_id": order_id, "status": "unknown"}

    def get_position(self, symbol: str) -> Dict:
        self.ib.reqPositions()
        for pos in self.ib.positions():
            if pos.contract.symbol == symbol:
                return {
                    "symbol": symbol,
                    "size": pos.position,
                    "avg_price": pos.avgCost
                }
        return {"symbol": symbol, "size": 0.0, "avg_price": 0.0}

    def get_all_positions(self) -> Dict[str, Dict]:
        positions = {}
        self.ib.reqPositions()
        for pos in self.ib.positions():
            positions[pos.contract.symbol] = {
                "size": pos.position,
                "avg_price": pos.avgCost
            }
        return positions

    def get_account_info(self) -> Dict:
        account = self.ib.accountSummary()
        return {
            "cash": float(account.loc["NetLiquidation", "value"]),
            "buying_power": float(account.loc["AvailableFunds", "value"]),
            "margin": float(account.loc["MaintMarginReq", "value"]),
        }

    def get_last_price(self, symbol: str) -> float:
        contract = self._stock_contract(symbol)
        ticker = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(0.5)
        return ticker.last

    def get_bid_ask(self, symbol: str) -> Dict[str, float]:
        contract = self._stock_contract(symbol)
        ticker = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(0.5)
        return {"bid": ticker.bid, "ask": ticker.ask}

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        return []  # IB는 개별 체결 기록 접근이 제한적 → custom DB 필요

    def is_connected(self) -> bool:
        return self.ib.isConnected()

    def reconnect(self) -> None:
        self.ib.disconnect()
        time.sleep(1)
        self.ib.connect("127.0.0.1", 7497, clientId=1)
