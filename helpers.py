import json
import requests


def api_fetch(endpoint):
    settings = get_settings()

    headers = {"Authorization": "token " + settings['token']}

    response = requests.get(settings['url'] + endpoint, headers=headers)

    return response


def get_settings():
    settings = {}
    with open('secrets.json') as f:
        settings = json.load(f)
    return settings
