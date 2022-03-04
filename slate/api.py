import time

import requests


class API:
    def __init__(self, project_id, model_id, token):
        """
        Initialize the lower API class to handle requests

        :param project_id: The project id to associate the model with
        :param model_id: The model id to associate the model with
        :param token: The token to validate the model
        """

        self.__headers = {
            'projectid': project_id,
            'modelid': model_id,
            'token': token,
            'time': time.time()
        }

        self.__api_url = 'https://events.blankly.finance'
        self.__api_version = 'v1'

    def __assemble_route_components(self, components: list) -> str:
        """
        Create a list of components that are assembled into one usable API url
        :param components: Ex: ['backtest', 'status'] -> https://events.blankly.finance/v1/backtest/status
        :return: str
        """
        url = self.__api_url + '/' + self.__api_version
        for i in components:
            url += '/'
            url += i

        return url

    def __assemble_route(self, route: str) -> str:
        """
        Append the route to the base url. This just pulls the two strings together
        :param route: route='/v1/backtest/status' -> https://events.blankly.finance/v1/backtest/status
        :return: str
        """
        return self.__api_url + route

    def __update_time(self) -> None:
        """
        Update the time in the headers

        :return: None
        """
        self.__headers['time'] = time.time()

    def post(self, route, data: dict) -> dict:
        """
        Make a basic POST request at a route
        :param route: The route without the base /v1/backtest/status
        :param data: The data to post as a dictionary in the body
        :return: dict (exchange response)
        """
        route = self.__assemble_route(route)
        self.__update_time()
        return requests.post(route, data=data, headers=self.__headers).json()

    def get(self, route) -> dict:
        """
        Make a basic GET request at the given route
        :param route: The route without the base /time
        :return: dict (the exchange response)
        """
        route = self.__assemble_route(route)
        self.__update_time()
        return requests.get(route, headers=self.__headers).json()
