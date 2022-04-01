from slate.integrations.backtesting_py import BacktestingPy
from slate.integrations.bt_py import BtPy
from slate.integrations.jesse_ai import JesseAi


class Integrations:
    def __init__(self, slate, api):
        self.bt = BtPy(slate, api)
        self.backtesting = BacktestingPy(slate, api)
        self.jesse = JesseAi(slate, api)
