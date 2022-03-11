import json
import os


def load_auth():
    """
    Load the authentication from the .slate.json file or the environment variables of the instance
    """
    try:
        slate_config = open('./slate.json')
        config = json.loads(slate_config.read())

        return config['model_id'], config['api_key'], config['api_pass']
    except FileNotFoundError:
        def validate_env(env, name):
            if env is None:
                raise EnvironmentError(f"A slate.json was not found and was not able to find a definition for the "
                                       f"environment variable: {name}")

        model = os.getenv('SLATE_MODEL_ID')
        validate_env(model, 'SLATE_MODEL_ID')

        api_key = os.getenv('SLATE_API_KEY')
        validate_env(api_key, 'SLATE_API_KEY')

        api_pass = os.getenv('SLATE_API_PASS')
        validate_env(api_pass, 'SLATE_API_PASS')

        return model, api_key, api_pass


def assemble_base(base_route: str, route: str) -> str:
    """
    Simple utility to append two route strings

    :param base_route: Base route like events.blankly.finance
    :param route: Specific route like
    :return: Appended strings as routes

    TODO this can validate that it is a valid path
    """
    return base_route + route
