import slate.utils as utils
from slate.live.live import Live
from slate.api import API


class Slate:
    def __init__(self):
        self.project_id, self.model_id, self.__token = utils.load_auth()

        self.__api = API(self.project_id, self.model_id, self.__token)

        self.live = Live(self.__api)
