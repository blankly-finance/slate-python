from operator import itemgetter

import slate
from slate.integrations.common import b_id, DUMMY_METRICS, DUMMY_INDICATORS

try:
    import bt
    from bt.backtest import Result
except ImportError:
    pass


class BtPy:
    slate: 'slate.Slate'
    api: 'slate.api.API'

    def __init__(self, slate, api):
        self.slate = slate
        self.api = api

    def post_backtests(self, result: 'Result'):
        for backtest in result.backtest_list:
            self._post_backtest(result, backtest)

    def _post_backtest(self, result: 'Result', backtest: 'Backtest'):
        symbols = [sym.upper() for sym in backtest.data.columns]
        quote = 'USD'
        for symbol in symbols:
            self.slate.model.add_symbol(symbol)
            if '-' in symbol:
                quote = symbol.split('_')[1]

        account_values = result \
            .prices[backtest.name] \
            .reset_index() \
            .rename(columns={'index': 'time', backtest.name: 'value'})
        account_values['time'] = account_values['time'].map(lambda t: t.timestamp())
        account_values = account_values.sort_values('time', ascending=True)
        account_values = account_values.to_dict('records')

        trades = result \
            .get_transactions(backtest.name) \
            .apply(map_trade, axis=1, result_type='expand') \
            .to_dict('records')

        id = b_id()
        start = result.stats[backtest.name]['start'].timestamp()
        end = result.stats[backtest.name]['end'].timestamp()
        self.slate.backtest.result(symbols=symbols,
                                   quote_asset=quote,
                                   start_time=start,
                                   stop_time=end,
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


def map_trade(row):
    time, symbol = row.name
    return {'time': time.timestamp(),
            'side': 'buy' if row['quantity'] > 0 else 'sell',
            'symbol': symbol.upper(),
            'price': row['price'],
            'size': abs(row['quantity']),
            'id': b_id(),
            'type': 'market'}


if __name__ == '__main__':
    # run bt.py backtest
    from bt import Strategy, Backtest

    data = bt.get('spy,agg', start='2010-01-01')
    strategy = Strategy('s1', [bt.algos.RunMonthly(),
                               bt.algos.SelectAll(),
                               bt.algos.WeighEqually(),
                               bt.algos.Rebalance()])
    backtest = Backtest(strategy, data)
    result = bt.run(backtest)

    # post to slate
    slate = slate.Slate()
    slate.integrations.bt.post_backtests(result)
