import hashlib
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


def create_md5(content):
    md5 = hashlib.md5()
    md5.update(content.encode("utf-8"))

    return md5.hexdigest()


def format_price(price):
    if price % 1 == 0:
        return int(price)
    return price


def get_settings():
    settings = {}
    with open('secrets.json') as f:
        settings = json.load(f)
    return settings
