import slate

try:
    import jesse
except ImportError:
    pass


class JesseAi:
    slate: 'slate.Slate'
    api: 'slate.api.API'

    def __init__(self, slate, api):
        self.slate = slate
        self.api = api

    def post_backtest(self, result):
        raise NotImplementedError


if __name__ == '__main__':
    # run jesse.ai backtest
    import jesse.helpers as jh
    from jesse.strategies import Strategy
    from jesse import utils
    from jesse.research import backtest, candles_from_close_prices

    prices01 = [10, 11, 12, 12, 11, 13, 14, 12, 11, 15]
    fake_candles01 = candles_from_close_prices(prices01)


    class ResearchStrategy(Strategy):
        def should_long(self):
            return True

        def should_short(self):
            return False

        def should_cancel(self):
            return True

        def go_long(self):
            entry_price = self.price
            qty = utils.size_to_qty(self.capital * 0.5, entry_price)
            self.buy = qty, entry_price

        def go_short(self):
            pass


    exchange_name = 'Fake Exchange'
    symbol = 'BTC-USDT'
    timeframe = '1m'
    config = {'starting_balance': 10_000,
              'fee': 0,
              'futures_leverage': 2,
              'futures_leverage_mode': 'cross',
              'exchange': exchange_name,
              'settlement_currency': 'USDT',
              'warm_up_candles': 0}
    routes = [{'exchange': exchange_name,
               'strategy': ResearchStrategy,
               'symbol': symbol,
               'timeframe': timeframe}]
    extra_routes = []
    candles = {
        jh.key(exchange_name, symbol): {'exchange': exchange_name,
                                        'symbol': symbol,
                                        'candles': fake_candles01}
    }

    result = backtest(config, routes, extra_routes, candles)

    # post to slate
    slate = slate.Slate()
    slate.integrations.jesse.post_backtest(result)
