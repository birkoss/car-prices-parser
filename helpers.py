import json
import requests


def api_get(endpoint):
    settings = get_settings()

    headers = {"Authorization": "token " + settings['token']}

    response = requests.get(settings['url'] + endpoint, headers=headers)

    return response


def api_post(endpoint, data):
    settings = get_settings()

    headers = {"Authorization": "token " + settings['token']}

    response = requests.post(
        settings['url'] + endpoint,
        data=data, headers=headers
    )

    return response


def create_logs():
    return {
        "debug": "",
        "error": "",
    }


def get_settings():
    settings = {}
    with open('secrets.json') as f:
        settings = json.load(f)
    return settings


def print_separator():
    print("------------------------------------------------")
