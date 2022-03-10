from slate.api import API
from slate.utils import assemble_base


class Model:
    def __init__(self, api: API):
        """
        Initialize a new live instance
        :param api: The object containing the Blankly API
        """
        self.__api: API = api

        self.__live_base = '/v1/model'

    def __assemble_base(self, route: str) -> str:
        """
        Assemble the sub-route specific to live posts

        :param route: The sub route: /spot-market -> /v1/live/spot-market
        :return: str
        """
        return assemble_base(self.__live_base, route)

    def set_lifecycle(self,
                      message: str = None,
                      start_at: [int, float] = None,
                      end_at: [int, float] = None,
                      running: bool = None) -> dict:
        """
        Update the model lifecycle
        All keys are optional so that any individual parameter can be updated
        https://docs.blankly.finance/services/events#post-v1modellifecycle

        :param message: A short message about status like 'Installing Dependencies'
        :param start_at: The start time in epoch
        :param end_at: The end time in epoch
        :param running: A boolean specifying if the model is running or not
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/lifecycle'), {
            'message': message,
            'start_at': start_at,
            'end_at': end_at,
            'running': running
        })

    # TODO add routes to remove the used symbols and exchanges
    def add_symbol(self,
                   symbol: str) -> dict:
        """
        Add a used symbol for the live view to the platform

        :param symbol: A string like 'AAPL' or 'BTC-USD'
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/used-symbol'), {
            'symbol': symbol
        })

    def set_exchange(self, used_exchange) -> dict:
        """
        Add an exchange to the list of used exchanges to the platform

        :param used_exchange: Exchange like 'coinbase_pro' or 'oanda'
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/used-exchange'), {
            'exchange': used_exchange
        })
