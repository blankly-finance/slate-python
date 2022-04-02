import json
from operator import itemgetter

import slate
from slate.integrations.common import b_id, DUMMY_METRICS, DUMMY_INDICATORS

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

    def post_backtest(self, json_result: str):
        with open(json_result, 'r') as file:
            trades = json.load(file)['trades']

        trades = [trade for j_trade in trades for trade in map_trades(j_trade)]
        trades.sort(key=itemgetter('time'))

        account_values = []
        current_value = 0
        for trade in trades:
            if 'PNL' in trade:
                current_value += trade['PNL']
                account_values.append({
                    'time': trade['time'],
                    'value': current_value
                })

        symbols = list({trade['symbol'] for trade in trades})
        quote_asset = symbols[0].split('-')[1] if '-' in symbols[0] else 'USD'
        start = trades[0]['time']
        end = trades[-1]['time']
        id = b_id()

        self.slate.backtest.result(symbols=symbols,
                                   quote_asset=quote_asset,
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


def map_trades(trade):
    common = {
        'symbol': trade['symbol'],
        'size': trade['size'],
        'type': 'market'
    }
    open = {**common,
            'time': trade['opened_at'],
            'side': 'buy' if trade['type'] == 'long' else 'sell',
            'price': trade['entry_price'],
            'id': b_id()}
    close = {**common,
             'time': trade['closed_at'],
             'side': 'sell' if trade['type'] == 'long' else 'buy',
             'price': trade['exit_price'],
             'id': b_id(),
             'PNL': trade['PNL']}  # used to calculate account values
    return [open, close]


if __name__ == '__main__':
    # post jesse-ai backtest to slate
    slate = slate.Slate()
    slate.integrations.jesse.post_backtest('backtest.json')
