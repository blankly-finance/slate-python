import slate

try:
    import bt
except ImportError:
    pass


class BtPy:
    slate: 'slate.Slate'
    api: 'slate.api.API'

    def __init__(self, slate, api):
        self.slate = slate
        self.api = api

    def post_backtest(self, result: 'bt.backtest.Result'):
        raise NotImplementedError


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
    slate.integrations.bt.post_backtest(result)
