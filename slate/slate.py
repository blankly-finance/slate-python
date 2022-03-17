import asyncio
import datetime
import time
import typing

import slate.utils as utils
from slate.api import API

from slate.live.live import Live
from slate.model.model import Model
from slate.backtest.backtest import Backtest


class Slate:
    def __init__(self, enable_async=False):
        """
        Initialize a new slate instance

        :param enable_async: Enable this to allow submission to the event loop
        """

        self.model_id, self.__api_key, self.__api_pass = utils.load_auth()

        self.__api = API(self.model_id, self.__api_key, self.__api_pass)

        self.live = Live(self.__api)
        self.model = Model(self.__api)
        self.backtest = Backtest(self.__api)

        self.__settings = {
            'enable_async': enable_async
        }
        self.__event_loop = None
        if enable_async:
            self.__event_loop = asyncio.get_event_loop()
            self.__event_loop.run_forever()

    def set_global_time(self, new_time: datetime.datetime = None):
        """
        Set the global time for slate. This will mean that any API requests done with a time pushed into this setting
        will be recorded at that time. If nothing is passed it will go back to using the live time
        :param new_time: A datetime object containing the global time
        :return: None
        """
        self.__api.time_setting = new_time

    def submit(self, callable_: typing.Callable, **kwargs):
        """
        Submit a new job into the slate-managed event loop. Ensure that the enable_async is == True on the
         initialization

        :param callable_: The function to submit to the event loop
        :param kwargs: A key/value set of arguments for the function to evaluate
        :return:
        """
        if self.__event_loop is not None:
            self.__event_loop.create_task(self.__execute(callable_, kwargs))
        else:
            raise Exception("Must set enable_sync to True to submit to the event loop")

    @staticmethod
    async def __execute(callable_: typing.Callable, kwargs: dict):
        """
        Execute the function in the event loop

        :param callable_: The function to submit to the event loop
        :param kwargs: A key/value set of arguments for the function to evaluate
        :return:
        """
        return callable_(**kwargs)

    @property
    def now(self):
        return time.time()
