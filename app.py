import ssl
import websocket
import json

SYMBOL = "BTCUSD"


class Orderbook():
    def __init__(self):
        self.orderbook = {
            'bid': {},
            'ask': {}
        }
        self.best_bid = (0, 0)
        self.best_ask = (0, 0)

    def update_records(self, events):
        for e in events:
            side, price, remaining = e['side'], float(e['price']), float(e['remaining'])
            if remaining == 0:
                del self.orderbook[side][price]
            else:
                self.orderbook[side][price] = remaining

    def print_orderbook(self, n=10):
        print('*' * 30)
        keys = sorted(list(self.orderbook['ask'].keys()))
        for key in reversed(keys[:n]):
            print(f"\t\t{key}\t{round(self.orderbook['ask'][key], 5)}")

        keys = sorted(list(self.orderbook['bid'].keys()), reverse=True)
        for key in keys[:n]:
            print(f"{round(self.orderbook['bid'][key], 5)}\t{key}")
        print('*' * 30)

    def update_best(self):
        updated = False
        bid = max(list(self.orderbook['bid'].keys()))
        bid_remaining = self.orderbook['bid'][bid]
        ask = min(list(self.orderbook['ask'].keys()))
        ask_remaining = self.orderbook['ask'][ask]

        if bid != self.best_bid[0] or bid_remaining != self.best_bid[1]:
            self.best_bid = (bid, bid_remaining)
            updated = True
        if ask != self.best_ask[0] or ask_remaining != self.best_ask[1]:
            self.best_ask = (ask, ask_remaining)
            updated = True

        if updated:
            print(f"{format(bid, '.2f')} {format(bid_remaining, '.8f')}"
                  " - "
                  f"{format(ask, '.2f')} {format(ask_remaining, '.8f')}", end='\r')


def on_message(ws, message):
    data = json.loads(message)
    events = data['events']
    if len(events) == 0:
        return
    e = events[0]
    reason = e['reason']

    if reason == 'initial':
        book.update_records(events)
        book.print_orderbook()
    elif reason in ('place', 'cancel'):
        book.update_records(events)
    book.update_best()


book = Orderbook()
ws = websocket.WebSocketApp(f"wss://api.gemini.com/v1/marketdata/{SYMBOL}", on_message=on_message)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
