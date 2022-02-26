import slate.utils as utils


class Slate:
    def __init__(self):
        self.project, self.model, self.__token = utils.load_auth()
