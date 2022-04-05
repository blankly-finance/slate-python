from operator import itemgetter

import pandas as pd

import slate
from slate.integrations.common import b_id, DUMMY_METRICS, DUMMY_INDICATORS

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

        trades = result['_trades'] \
            .apply(map_trades, axis=1, result_type='expand', symbol=symbol) \
            .unstack() \
            .reset_index(drop=True) \
            .apply(pd.Series) \
            .sort_values('time', ascending=True) \
            .to_dict('records')

        equity = result['_equity_curve']['Equity']
        account_values = equity.loc[equity.shift() != equity] \
            .reset_index() \
            .rename(columns={'index': 'time', 'Equity': 'value'})
        account_values['time'] = account_values['time'].map(lambda t: t.timestamp())
        account_values = account_values.to_dict('records')

        id = b_id()
        self.slate.backtest.result(symbols=[symbol],
                                   quote_asset=quote,
                                   start_time=result['Start'].timestamp(),
                                   stop_time=result['End'].timestamp(),
                                   account_values=account_values,
                                   trades=trades,
                                   backtest_id=id,
                                   metrics=DUMMY_INDICATORS,
                                   indicators=DUMMY_METRICS)

        self.slate.backtest.status(backtest_id=id,
                                   successful=True,
                                   status_summary='Completed',
                                   status_details='',
                                   time_elapsed=0)


def map_trades(row: pd.Series, symbol: str) -> list:
    common = {'symbol': symbol,
              'size': abs(row['Size']),
              'type': 'market'}
    entry = {**common,
             'time': row['EntryTime'].timestamp(),
             'side': 'buy' if row['Size'] > 0 else 'sell',
             'id': b_id(),
             'price': row['EntryPrice']}
    exit = {**common,
            'time': row['ExitTime'].timestamp(),
            'side': 'sell' if row['Size'] > 0 else 'buy',
            'id': b_id(),
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
