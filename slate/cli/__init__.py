"""
    Updated CLI for interacting with and uploading slate models.
    Copyright (C) 2022 Matias Kotlik

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import json
import os.path

import questionary
import sys
import traceback
import webbrowser
from pathlib import Path
from typing import Optional
import pkgutil

from questionary import Choice

from slate.cli.api import API, blankly_deployment_url
from slate.cli.deploy import zip_dir, get_python_version
from slate.cli.login import logout, poll_login, get_token
from slate.cli.ui import text, confirm, print_work, print_failure, print_success, select, show_spinner

AUTH_URL = 'https://app.blankly.finance/auth/signin?redirectUrl=/deploy'


def validate_non_empty(text):
    if not text.strip():
        return 'Please enter a value'
    return True


def create_model(api, name, description, model_type, project_id=None):
    with show_spinner('Creating model') as spinner:
        try:
            model = api.create_model(project_id or api.user_id, model_type, name, description)
        except Exception:
            spinner.fail('Failed to create model')
            raise
        spinner.ok('Created model')
    return model


def ensure_login() -> API:
    # TODO print selected team ?
    api = is_logged_in()
    if api:
        return api
    return launch_login_flow()


def is_logged_in() -> Optional[API]:
    token = get_token()
    if not token:
        return

    # log into deployment api
    try:
        return API(token)
    except Exception:  # TODO
        return


def launch_login_flow() -> API:
    try:
        webbrowser.open_new(AUTH_URL)
        print_work(f'Your browser was opened to {AUTH_URL}. Open the window and login.')
    except Exception:
        print_work(f'Could not find a browser to open. Navigate to {AUTH_URL} and login')

    api = None
    with show_spinner(f'Waiting for login') as spinner:
        try:
            api = poll_login()
        except Exception:
            pass  # we just check for api being valid, poll_login can return None

        if not api:
            spinner.fail('Failed to login')
            sys.exit(1)

        spinner.ok('Logged in')
    return api


def slate_init(args):
    dir_is_empty = len([f for f in os.listdir() if not f.startswith('.')]) == 0
    api = ensure_login()
    model = get_model_interactive(api)

    if dir_is_empty:
        script_path = './main.py'
    else:
        script_path = questionary.path('What is the main script or entry point? (ex: main.py, bot.py)').unsafe_ask()

    with show_spinner('Generating files') as spinner:
        files = [
            ('slate.json', generate_slate_json(model, api), False),
            ('blankly.json', generate_blankly_json(model, script_path), False),
            (script_path, "if __name__ == '__main__':\n    print('Hello, World!')\n", True),
            ('requirements.txt', 'slate\n', True),
        ]
        spinner.ok('Generated files')

    for path, data, skip_existing in files:
        exists = Path(path).exists()
        if skip_existing and exists:
            continue
        if exists and not confirm(f'{path} already exists, would you like to overwrite it?',
                                  default=False).unsafe_ask():
            continue
        with open(path, 'w') as file:
            file.write(data)

    print_success('Your model was created. Run `slate deploy` to deploy it to slate.')


def ensure_model(api: API):
    # create model if it doesn't exist
    try:
        with open('blankly.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print_failure('There was no model detected in this directory. Try running `slate init` to create one')
        sys.exit(1)

    if 'plan' not in data:
        data['plan'] = select('Select a plan:', [Choice(f'{name} - CPU: {info["cpu"]} RAM: {info["ram"]}', name)
                                                 for name, info in api.get_plans('live').items()]).unsafe_ask()

    if 'model_id' not in data or 'project_id' not in data:
        model = get_model_interactive(api)
        data['model_id'] = model['modelId']
        data['project_id'] = model['projectId']

    # save model_id and plan back into blankly.json
    with open('blankly.json', 'w') as file:
        json.dump(data, file, indent=4)

    return data


def missing_deployment_files(data) -> list:
    paths = [data['main_script'], 'slate.json', 'blankly.json', 'requirements.txt']
    return [path for path in paths if not Path(path).is_file()]


def slate_deploy(args):
    api = ensure_login()

    data = ensure_model(api)
    for path in missing_deployment_files(data):
        if not confirm(f'{path} is missing. Are you sure you want to continue?',
                       default=False).unsafe_ask():
            print_failure('Deployment cancelled')
            print_failure(f'You can try `slate init` to regenerate the {path} file.')
            return

    description = text('Enter a description for this version of the model:').unsafe_ask()

    with show_spinner('Uploading model') as spinner:
        model_path = zip_dir('.', data['ignore_files'])

        params = {
            'file_path': model_path,
            'project_id': data['project_id'],  # set by ensure_model
            'model_id': data['model_id'],  # set by ensure_model
            'version_description': description,
            'python_version': get_python_version(),
            'type_': data.get('type', 'strategy'),
            'plan': data['plan']  # set by ensure_model
        }
        if data.get('type', None) == 'screener':
            params['schedule'] = data['screener']['schedule']

        response = api.deploy(**params)
        if response.get('status', None) == 'success':
            spinner.ok('Model uploaded')
        else:
            spinner.fail('Error: ' + response['error'])


def get_model_interactive(api):
    create = select('Would you like to create a new model or attach to an existing one?',
                    [Choice('Create new model', True), Choice('Attach to existing model', False)]).unsafe_ask()
    if create:
        default_name = Path.cwd().name  # default name is working dir name
        name = text('Model name?', default=default_name, validate=validate_non_empty).unsafe_ask()
        description = text('Model description?', instruction='(Optional)').unsafe_ask()
        teams = api.list_teams()
        team_id = None
        if teams:
            team_choices = [Choice('Create on my personal account', False)] \
                           + [Choice(team.get('name', team['id']), team['id']) for team in teams]
            team_id = select('What team would you like to create this model under?', team_choices).unsafe_ask()
            return create_model(api, name, description, 'strategy', team_id or None)

    with show_spinner('Loading models...') as spinner:
        models = api.list_all_models()
        spinner.ok('Loaded')

    model = select('Select an existing model to attach to:',
                   [Choice(get_model_repr(model), model) for model in models]).unsafe_ask()
    return model


def get_model_repr(model: dict) -> str:
    name = model.get('name', model['id'])
    team = model.get('team', {}).get('name', None)
    if team:
        name = team + ' - ' + name
    return name


def generate_blankly_json(model: dict, script: str):
    data = {'main_script': script,
            'python_version': get_python_version(),
            'requirements': './requirements.txt',
            'working_directory': '.',
            'model_id': model['id'],
            'project_id': model['projectId'],
            'ignore_files': ['.git', '.idea', '.vscode']}
    return json.dumps(data, indent=4)


def generate_slate_json(model: dict, api: API):
    project_id = model['projectId']
    project_keys = api.generate_keys(project_id)
    data = {
        'api_key': project_keys['apiKey'],
        'api_pass': project_keys['apiPass'],
        'model_id': model['id'],
        'project_id': project_id
    }
    return json.dumps(data, indent=4)


def slate_login(args):
    if is_logged_in():
        print_success('You are already logged in')
        return

    launch_login_flow()


def slate_logout(args):
    with show_spinner('Logging out of Slate') as spinner:
        try:
            logout()
        except Exception:
            spinner.fail('Failed to logout')
            raise
        spinner.ok('Logged out')


def main():
    parser = argparse.ArgumentParser(description='Slate CLI')
    subparsers = parser.add_subparsers(required=True)

    init_parser = subparsers.add_parser('init', help='Initialize a slate model in the current directory')
    init_parser.set_defaults(func=slate_init)

    deploy_parser = subparsers.add_parser('deploy', help='Deploy a new version of your model to slate')
    deploy_parser.set_defaults(func=slate_deploy)

    login_parser = subparsers.add_parser('login', help='Login to Slate')
    login_parser.set_defaults(func=slate_login)

    logout_parser = subparsers.add_parser('logout', help='Logout of Slate')
    logout_parser.set_defaults(func=slate_logout)

    # run the selected command
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print_failure('Cancelled by user')
    except Exception:
        print_failure('An error occurred. Traceback:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
