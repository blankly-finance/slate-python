import datetime
import json
import os
from uuid import uuid4
import pandas as pd
import numpy as np

from slate.api import API
from slate.utils import assemble_base


class Backtest:
    def __init__(self, api: API):
        """
        Initialize a new live instance
        :param api: The object containing the Blankly API
        """
        self.__api: API = api

        self.__live_base = '/v1/backtest'

    def __assemble_base(self, route: str) -> str:
        """
        Assemble the sub-route specific to live posts

        :param route: The sub route: /spot-market -> /v1/live/spot-market
        :return: str
        """
        return assemble_base(self.__live_base, route)

    @staticmethod
    def generate_new_backtest_id() -> str:
        """
        Create a new unique backtest identifier

        :return: A string uuid which can be used for backtesting
        """

        # Import UUID here to reduce load time
        import uuid
        return str(uuid.uuid4())

    def result(self,
               symbols: list,
               quote_asset: str,
               start_time: [int, float, datetime.datetime],
               stop_time: [int, float, datetime.datetime],
               account_values: [list, pd.Series, np.ndarray],
               trades: [list, pd.Series, np.ndarray],
               exchange: str,
               backtest_id: str = None,
               metrics: dict = None,
               indicators: dict = None,
               time: datetime.datetime = None
               ) -> dict:
        """
        Post a backtest result object to the platform

        **Look at this link to learn more**:
        https://docs.blankly.finance/services/events#post-v1backtestresult
        """
        if backtest_id is None:  # generate one if they don't input one
            backtest_id = str(uuid4())

        # Convert any ndarray
        if isinstance(account_values, np.ndarray):
            account_values = account_values.tolist()
        if isinstance(trades, np.ndarray):
            trades = trades.tolist()

        if isinstance(account_values, pd.Series):
            account_values = account_values.tolist()
        if isinstance(trades, pd.Series):
            trades = trades.tolist()

        if isinstance(start_time, datetime.datetime):
            start_time = start_time.timestamp()
        if isinstance(stop_time, datetime.datetime):
            stop_time = stop_time.timestamp()

        data = {
            'symbols': symbols,
            'quote_asset': quote_asset,
            'start_time': start_time,
            'stop_time': stop_time,
            'account_values': account_values,
            'trades': trades,
            'exchange': exchange,
            'metrics': metrics,
            'backtest_id': backtest_id,
            'indicators': indicators,
        }
        files = {}
        if len(account_values) > 0:
            import tempfile
            account_values_json = {
                'account_values': account_values
            }
            fd, path = tempfile.mkstemp()
            open(path, 'w').write(json.dumps(account_values_json, indent=2))
            os.close(fd)
            files['account_values'] = path
            data.pop('account_values')
        if len(trades) > 0:
            import tempfile
            trades_json = {
                'trades': trades
            }
            fd, path = tempfile.mkstemp()
            open(path, 'w').write(json.dumps(trades_json, indent=2))
            os.close(fd)
            files['trades'] = path
            data.pop('trades')

        return self.__api.post(self.__assemble_base('/result'), data, time, files_=files)

    def status(self,
               successful: bool,
               status_summary: str,
               status_details: str,
               time_elapsed: [int, float],
               backtest_id: str,
               description: str = None,
               label: str = None,
               time: datetime.datetime = None) -> dict:
        """
        Post a backtest status. This is primarily used for backtest lifecycle
        https://docs.blankly.finance/services/events#post-v1livelog

        :param successful: A boolean specifying if it succeeds or fails
        :param status_summary: A brief message if the status has completed or not
        :param status_details: A more extensive message about the backtest
        :param time_elapsed: The amount of time taken to start and run the backtest
        :param backtest_id: The identifier for the backtest
        :param time: A time object to fill if the event occurred in the past
        :param description: Post or overwrite the backtest description
        :param label: Add a label to your backtest. Should be short.
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/status'), {
            'successful': successful,
            'status_summary': status_summary,
            'status_details': status_details,
            'time_elapsed': time_elapsed,
            'backtest_id': backtest_id,
            'description': description,
            'label': label
        }, time)

    def log(self, line: str, type_: str, backtest_id: str, time: datetime.datetime = None) -> dict:
        """
        Post a new log from a backtesting model. This can be stdout or any custom logs
        https://docs.blankly.finance/services/events#post-v1backtestlog

        :param line: The line to write
        :param type_: The type of line, common types include 'stdout' or 'stderr'
        :param backtest_id: The identifier for the backtest
        :param time: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """
        return self.__api.post('/log', {
            'line': line,
            'type': type_,
            'backtest_id': backtest_id
        }, time)
