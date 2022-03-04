from slate.api import API


class Live:
    def __init__(self, api: API):
        """
        Initialize a new live instance
        :param api: The object containing the Blankly API
        """
        self.__backtest_id = None
        self.__api: API = api

        self.__live_base = '/v1/live'

    def update_backtest_id(self, new_backtest_id: str) -> None:
        """
        Update the backtest id for this instance

        :param new_backtest_id: The new id to use
        :return: None
        """
        self.__backtest_id = new_backtest_id

    def __assemble_live_base(self, route: str) -> str:
        """
        Assemble the sub-route specific to live posts

        :param route: The sub route: /spot-market -> /v1/live/spot-market
        :return: str
        """
        return self.__live_base + route

    def event(self, args: dict, response: dict, type_: str, annotation: str = None):
        return self.__api.post(self.__assemble_live_base('/event'), {
            'args': args,
            'response': response,
            'type': type_,
            'annotation': annotation
        })
