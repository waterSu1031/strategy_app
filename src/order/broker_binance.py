import ccxt
from order_execution.broker_interface import BrokerInterface
from typing import Dict, List, Optional
import time

class BinanceBroker(BrokerInterface):
    def __init__(self, api_key: str, api_secret: str, use_futures: bool = True, testnet: bool = True):
        exchange_class = ccxt.binanceusdm if use_futures else ccxt.binance
        self.exchange = exchange_class({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True
        })
        self.use_futures = use_futures

        if testnet and use_futures:
            self.exchange.set_sandbox_mode(True)

    def send_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "market", price: Optional[float] = None,
                   tag: Optional[str] = None) -> Dict:
        side = side.lower()
        order_type = order_type.lower()
        params = {}

        try:
            if order_type == "limit":
                assert price is not None, "Limit order requires price"
                order = self.exchange.create_limit_order(symbol, side, quantity, price, params)
            elif order_type == "market":
                order = self.exchange.create_market_order(symbol, side, quantity, params)
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            return {
                "order_id": order["id"],
                "symbol": symbol,
                "side": side,
                "quantity": order["amount"],
                "price": order.get("average", order.get("price", None)),
                "status": order["status"],
                "tag": tag
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancel_order(self, order_id: str) -> bool:
        try:
            self.exchange.cancel_order(order_id)
            return True
        except Exception:
            return False

    def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        try:
            self.exchange.cancel_all_orders(symbol)
            return 1
        except Exception:
            return 0

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        orders = self.exchange.fetch_open_orders(symbol) if symbol else self.exchange.fetch_open_orders()
        return [{
            "order_id": o["id"],
            "symbol": o["symbol"],
            "side": o["side"],
            "quantity": o["amount"],
            "price": o["price"],
            "status": o["status"]
        } for o in orders]

    def get_order_status(self, order_id: str) -> Dict:
        try:
            all_orders = self.exchange.fetch_open_orders()
            for o in all_orders:
                if o["id"] == order_id:
                    return {
                        "order_id": o["id"],
                        "symbol": o["symbol"],
                        "status": o["status"],
                        "filled": o["filled"],
                        "remaining": o["remaining"]
                    }
        except Exception:
            pass
        return {"order_id": order_id, "status": "unknown"}

    def get_position(self, symbol: str) -> Dict:
        if self.use_futures:
            positions = self.exchange.fetch_positions([symbol])
            for pos in positions:
                if pos["symbol"] == symbol:
                    return {
                        "symbol": symbol,
                        "size": float(pos["contracts"]),
                        "avg_price": float(pos["entryPrice"])
                    }
        else:
            balance = self.exchange.fetch_balance()
            asset = symbol.split("/")[0]
            size = balance["free"].get(asset, 0.0)
            return {"symbol": symbol, "size": size, "avg_price": None}
        return {"symbol": symbol, "size": 0.0, "avg_price": None}

    def get_all_positions(self) -> Dict[str, Dict]:
        result = {}
        if self.use_futures:
            for pos in self.exchange.fetch_positions():
                size = float(pos["contracts"])
                if size != 0:
                    result[pos["symbol"]] = {
                        "size": size,
                        "avg_price": float(pos["entryPrice"])
                    }
        else:
            balance = self.exchange.fetch_balance()
            for asset, amount in balance["free"].items():
                if amount > 0:
                    result[asset] = {"size": amount, "avg_price": None}
        return result

    def get_account_info(self) -> Dict:
        balance = self.exchange.fetch_balance()
        return {
            "cash": balance["total"].get("USDT", 0.0),
            "positions": self.get_all_positions(),
            "total_equity": sum(balance["total"].values())
        }

    def get_last_price(self, symbol: str) -> float:
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker["last"]

    def get_bid_ask(self, symbol: str) -> Dict[str, float]:
        orderbook = self.exchange.fetch_order_book(symbol)
        return {
            "bid": orderbook["bids"][0][0] if orderbook["bids"] else 0.0,
            "ask": orderbook["asks"][0][0] if orderbook["asks"] else 0.0
        }

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        trades = self.exchange.fetch_my_trades(symbol, limit=limit) if symbol else []
        return [{
            "symbol": t["symbol"],
            "side": t["side"],
            "price": t["price"],
            "amount": t["amount"],
            "timestamp": t["timestamp"]
        } for t in trades]

    def is_connected(self) -> bool:
        try:
            self.exchange.check_required_credentials()
            return True
        except Exception:
            return False

    def reconnect(self) -> None:
        pass  # ccxt는 상태 유지형 연결이 아님

# from binance_broker import BinanceBroker
#
# broker = BinanceBroker(api_key="your_key", api_secret="your_secret", testnet=True)
#
# order = broker.send_order("BTC/USDT", "buy", 0.001, order_type="market")
# print(order)
