from operator import itemgetter

import pandas as pd
from backtesting._stats import _Stats

import slate
from slate.integrations.common import b_id

try:
    import backtesting
except ImportError:
    pass


class BacktestingPy:
    slate: 'slate.Slate'
    api: 'slate.api.API'

    def __init__(self, slate, api):
        self.slate = slate
        self.api = api

    def post_backtest(self, result: 'backtesting.Backtest', symbol: str = None):
        self.slate.model.add_symbol(symbol)
        symbol = symbol or 'Unknown'
        quote = symbol.split('-')[1] if '-' in symbol else 'USD'

        trades = [trade
                  for idx, row in result['_trades'].iterrows()
                  for trade in map_trades(symbol, row)]
        trades.sort(key=itemgetter('time'))

        account_values = result['_equity_curve']['Equity']
        account_values = account_values.loc[account_values.shift() != account_values]
        account_values = [{'time': time.timestamp(),
                           'value': value}
                          for time, value in account_values.items()]

        # events api does this for us. oops!
        # metrics_key_map = {'Return [%]': 'cum_returns',
        #                    'Return (Ann.) [%]': 'cagr',
        #                    'Volatility (Ann.) [%]': 'volatility',
        #                    'Sharpe Ratio': 'sharpe',
        #                    'Sortino Ratio': 'sortino',
        #                    'Calmar Ratio': 'calmar',
        #                    'Max. Drawdown [%]': 'max_drawdown'}
        #
        # metrics = {blankly_key: {'value': result[metrics_key],
        #                          'display_name': metrics_key,
        #                          'type': 'percent' if '%' in metrics_key else 'ratio'}
        #            for metrics_key, blankly_key in metrics_key_map.items()}

        id = b_id()
        self.slate.backtest.result(symbols=[symbol],
                                   quote_asset=quote,
                                   start_time=result['Start'].timestamp(),
                                   stop_time=result['End'].timestamp(),
                                   account_values=account_values,
                                   trades=trades,
                                   backtest_id=id,
                                   metrics=[],
                                   indicators=[])

        self.slate.backtest.status(backtest_id=id,
                                   successful=True,
                                   status_summary='Completed',
                                   status_details='',
                                   time_elapsed=0)


def map_trades(symbol: str, row: pd.Series) -> list:
    common = {'symbol': symbol,
              'size': abs(row['Size']),
              'type': 'market', }
    entry = {**common, 'side': 'buy' if row['Size'] > 0 else 'sell',
             'id': b_id(),
             'time': row['EntryTime'].timestamp(),
             'price': row['EntryPrice']}
    exit = {**common, 'side': 'sell' if row['Size'] > 0 else 'buy',
            'id': b_id(),
            'time': row['ExitTime'].timestamp(),
            'price': row['ExitPrice']}
    return [entry, exit]


if __name__ == '__main__':
    # run backtesting.py backtest
    from backtesting import Backtest, Strategy
    from backtesting.lib import crossover
    from backtesting.test import SMA, GOOG


    class SmaCross(Strategy):
        n1 = 10
        n2 = 20

        def init(self):
            close = self.data.Close
            self.sma1 = self.I(SMA, close, self.n1)
            self.sma2 = self.I(SMA, close, self.n2)

        def next(self):
            if crossover(self.sma1, self.sma2):
                self.buy()
            elif crossover(self.sma2, self.sma1):
                self.sell()


    bt = Backtest(GOOG, SmaCross,
                  cash=10000, commission=.002,
                  exclusive_orders=True)
    result = bt.run()

    # post to slate
    slate = slate.Slate()
    slate.integrations.backtesting.post_backtest(result, 'GOOG')
