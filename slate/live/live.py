import datetime
import json
import warnings

from slate.api import API
from slate.utils import assemble_base


class Live:
    def __init__(self, api: API):
        """
        Initialize a new live instance
        :param api: The object containing the Blankly API
        """
        self.__api: API = api

        self.__live_base = '/v1/live'

    def __assemble_base(self, route: str) -> str:
        """
        Assemble the sub-route specific to live posts

        :param route: The sub route: /spot-market -> /v1/live/spot-market
        :return: str
        """
        return assemble_base(self.__live_base, route)

    def event(self, args: dict, response: dict, type_: str, annotation: str = None,
              time: datetime.datetime = None) -> dict:
        """
        Post an event to the platform - generally used for annotating & viewing any important custom function calls
        https://docs.blankly.finance/services/events/#post-v1liveupdate-trade

        :param args: The (function) arguments
        :param response: The (function) response
        :param type_: A custom type for the event like 'order' or 'check_price'
        :param annotation: A human-friendly bit of text for your function
        :param time: A time object to fill if the event occurred in the past
        :return: API Response
        """
        return self.__api.post(self.__assemble_base('/event'), {
            'args': args,
            'response': response,
            'type': type_,
            'annotation': annotation
        }, time)

    def spot_market(self,
                    symbol: str,
                    exchange: str,
                    id_: str,
                    side: str,
                    size: [float, int] = None,
                    funds: [float, int] = None,
                    annotation: str = None,
                    time: datetime.datetime = None) -> dict:
        """
        Post a market order done on a spot exchange to the platform
        https://docs.blankly.finance/services/events/#post-v1liveupdate-trade

        :param symbol: The symbol the order is under
        :param exchange: The exchange the order was performed on - ex: 'coinbase_pro' or 'alpaca'
        :param id_: The exchange-given order id
        :param side: The side - 'buy' or 'sell'
        :param size: Mutually exclusive with funds - if you place an order priced in the base asset
        :param funds: Mutually exclusive with size - if you place an order priced in the quote asset
        :param annotation: An optional annotation to be given to this order
        :param time: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/spot-market'), {
            'symbol': symbol,
            'id': id_,
            'side': side,
            'exchange': exchange,
            'size': size,
            'funds': funds,
            'annotation': annotation
        }, time)

    def spot_limit(self,
                   symbol: str,
                   exchange: str,
                   id_: str,
                   side: str,
                   price: [int, float],
                   size: [float, int] = None,
                   funds: [float, int] = None,
                   annotation: str = None,
                   time: datetime.datetime = None):
        """
        Post a limit order done on a spot exchange to the platform
        https://docs.blankly.finance/services/events/#post-v1liveupdate-trade

        :param symbol: The symbol the order was placed on
        :param exchange: The exchange the order was performed on - ex: 'coinbase_pro' or 'alpaca'
        :param id_: The exchange-generated order id
        :param side: The order side - 'buy' or 'sell'
        :param price: The limit order price
        :param size: Mutually exclusive with funds - if you place an order priced in the base asset
        :param funds: Mutually exclusive with size - if you place an order priced in the quote asset
        :param annotation: An optional annotation to be given to this order
        :param time: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/spot-limit'), {
            'symbol': symbol,
            'id': id_,
            'side': side,
            'exchange': exchange,
            'price': price,
            'size': size,
            'funds': funds,
            'annotation': annotation
        }, time)

    def spot_stop(self,
                  symbol: str,
                  exchange: str,
                  id_: str,
                  side: str,
                  price: [int, float],
                  activate: [int, float],
                  size: [float, int] = None,
                  funds: [float, int] = None,
                  annotation: str = None,
                  time: datetime.datetime = None):
        """
        Post a limit order done on a spot exchange to the platform
        https://docs.blankly.finance/services/events/#post-v1liveupdate-trade

        :param symbol: The symbol the order was placed on
        :param exchange: The exchange the order was performed on - ex: 'coinbase_pro' or 'alpaca'
        :param id_: The exchange-generated order id
        :param side: The order side - 'buy' or 'sell'
        :param price: The limit order price
        :param activate: The activation price of the stop order
        :param size: Mutually exclusive with funds - if you place an order priced in the base asset
        :param funds: Mutually exclusive with size - if you place an order priced in the quote asset
        :param annotation: An optional annotation to be given to this order
        :param time: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """
        return self.__api.post(self.__assemble_base('/spot-limit'), {
            'symbol': symbol,
            'id': id_,
            'side': side,
            'exchange': exchange,
            'price': price,
            'activate': activate,
            'size': size,
            'funds': funds,
            'annotation': annotation,
        }, time)

    def update_trade(self, id_: str, **kwargs) -> dict:
        """
        Update an existing trade on the platform by order ID
        https://docs.blankly.finance/services/events/#post-v1liveupdate-trade

        :param id_: The exchange-given order id
        :param kwargs: Any key/value pair. Generally these should be the same as the above order keys
        :return: API Response (dict)
        """
        kwargs['id'] = id_
        return self.__api.post(self.__assemble_base('/update-trade'), kwargs)

    def update_annotation(self, id_: str, annotation: str) -> dict:
        """
        Explicitly update just the order annotation
        https://docs.blankly.finance/services/events/#post-v1liveupdate-annotation

        :param id_: The exchange-given order id
        :param annotation: A descriptor about the order
        :return: API Response (dict)
        """
        return self.__api.post(self.__assemble_base('/update-annotation'), {
            'id': id_,
            'annotation': annotation
        })

    def screener_result(self, result: dict, time_: datetime.datetime = None) -> dict:
        """
        Post a screener result to the platform
        https://docs.blankly.finance/services/events/#post-v1livescreener-result

        :param result: The screener results object
            example:
            {
                "AAPL": {              // Organize by symbol
                    "RSI": 29.5,       // Keep the same keys internally across all symbols
                    "buy_signal": true // Keep same keys
                },
                "MSFT": {
                    "RSI": 54.3,       // Nesting beyond this level is not supported
                    "buy_signal": false
                }
            }
        :param time_: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """

        # Test for double nesting in the results dictionary
        for i in result:
            inner = result[i]
            for j in inner:
                if isinstance(inner[j], dict):
                    warnings.warn(f"Double nested dictionaries are not supported in the screener result: "
                                  f"\n{json.dumps(inner[j], indent=2)}")

        # Format to API spec
        result = {'result': result}

        return self.__api.post(self.__assemble_base('/screener-result'), result, time_)

    def log(self, line: str, type_: str, time_: datetime.datetime = None) -> dict:
        """
        Post a new log from a live running model. This can be stdout or any custom logs
        https://docs.blankly.finance/services/events#post-v1livelog

        :param line: The line to write
        :param type_: The type of line, common types include 'stdout' or 'stderr'
        :param time_: A time object to fill if the event occurred in the past
        :return: API response (dict)
        """
        return self.__api.post('/log', {
            'line': line,
            'type': type_
        }, time_)
