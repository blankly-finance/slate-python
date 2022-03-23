import copy
import time
import requests
from slate.exceptions import APIException


class API:
    def __init__(self, model_id, api_key, api_pass):
        """
        Initialize the lower API class to handle requests

        :param model_id: The model id to associate the model with
        :param api_key: The API key for this project
        :param api_pass: The API pass for this project
        """

        self.__headers = {
            'model_id': model_id,
            'api_key': api_key,
            'api_pass': api_pass,
            'time': str(time.time())
        }

        # This is none for live but a datetime when set
        self.time_setting = None

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

    def __update_time(self, time_) -> dict:
        """
        Update the time in the headers

        :return: None
        """
        headers = copy.copy(self.__headers)
        if time_ is None:
            headers['time'] = str(time.time())
        else:
            headers['time'] = str(time_.timestamp())
        return headers

    @staticmethod
    def __check_errors(response: requests.Response) -> dict:
        # Check if the body is empty
        if response.raw._body is None:
            body = {}
        else:
            body = response.json()

        # Now if there is an error in the non-empty body throw an error
        # If not just return out
        if 'error' in body:
            raise APIException(body['error'])
        else:
            return body

    def post(self, route, data: dict, time_=None, files_: dict = None):
        """
        Make a basic POST request at a route
        :param route: The route without the base /v1/backtest/status
        :param data: The data to post as a dictionary in the body
        :param time_: A datetime to pass into the function
        :param files_: A dictionary containing key/values of files to file paths
        :return: dict (exchange response)
        """
        if files_ is not None:
            for i in files_:
                files_[i] = open(files_[i], 'rb')
        else:
            files_ = {}

        route = self.__assemble_route(route)
        headers = self.__update_time(time_)
        response = requests.post(route, data=data, headers=headers, files=files_)
        return response  # self.__check_errors(response)

    def get(self, route, time_=None):
        """
        Make a basic GET request at the given route
        :param route: The route without the base /time
        :param time_: A datetime to pass into the function
        :return: dict (the exchange response)
        """
        route = self.__assemble_route(route)
        headers = self.__update_time(time_)
        return requests.get(route, headers=headers)
