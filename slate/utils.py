import json
import os


def load_auth():
    """
    Load the authentication from the .slate.json file or the environment variables of the instance
    """
    try:
        slate_config = open('./slate.json')
        config = json.loads(slate_config.read())

        return config['project_id'], config['model_id'], config['token']
    except FileNotFoundError:
        def validate_env(env, name):
            if env is None:
                raise EnvironmentError(f"A slate.json was not found and was not able to find a definition for the "
                                       f"environment variable: {name}")
        project = os.getenv('SLATE_PROJECT_ID')
        validate_env(project, 'SLATE_PROJECT_ID')

        model = os.getenv('SLATE_MODEL_ID')
        validate_env(model, 'SLATE_MODEL_ID')

        token = os.getenv('SLATE_TOKEN')
        validate_env(token, 'SLATE_TOKEN')

        return project, model, token


def assemble_base(base_route: str, route: str) -> str:
    """
    Simple utility to append two route strings

    :param base_route: Base route like events.blankly.finance
    :param route: Specific route like
    :return: Appended strings as routes

    TODO this can validate that it is a valid path
    """
    return base_route + route
