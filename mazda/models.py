import html
import json
import requests
import sys

from helpers import api_get, api_post
from logs import Logs


def run():
    logs = Logs()

    # API - Fetch the models
    models_url = "make/mazda/models"
    logs.debug("API - Fetching models")
    response = api_get(models_url)
    if response.status_code != 200:
        logs.error("API - Cannot fetch models - Status code: " + response.status_code)  # nopep8
        return logs
    api_json = json.loads(response.content)
    api_models = api_json['models']

    # Mazda - Fetch the models
    logs.debug("Mazda - Fetching models")
    response = requests.get("https://www.mazda.ca/common/apps/assets/json/step1/qc.json?v=1547651328198")  # nopep8
    if response.status_code != 200:
        logs.error("Mazda - Cannot fetch models")
        return logs
    mazda_json = json.loads(response.content)

    # Mazda - Reformat models
    mazda_models = []
    for single_category in mazda_json['categories']:
        for single_model in single_category['carline']:
            for single_year in single_model['modelYear']:
                model = {
                    "name": single_model['carline'][0].upper() + single_model['carline'][1:].lower(),  # nopep8
                    "year": str(single_year['year']),
                    "foreign_id": single_model['carline'] + " " + str(single_year['year']),  # nopep8
                }
                mazda_models.append(model)

    # Mazda - Validate models
    if len(mazda_models) == 0:
        logs.error("Mazda - No models founds")
        return logs

    # Validate each Mazda models
    for mazda_model in mazda_models:
        existing_model = False
        for api_model in api_models:
            if mazda_model['foreign_id'] == api_model['foreign_id']:
                existing_model = True
        # - Create new model
        if not existing_model:
            response = api_post(models_url, {
                "name": mazda_model['name'],
                "year": mazda_model['year'],
                "foreign_id": mazda_model['foreign_id'],
            })
            if response.status_code == 200:
                logs.debug("API - Creating - " + mazda_model['name'] + " " + mazda_model['year'])  # nopep8
            else:
                logs.error("API - Cannot create model - " + mazda_model['name'] + " " + mazda_model['year'])  # nopep8

    # Warn about the API models not available anymore
    for api_model in api_models:
        available_model = False
        for mazda_model in mazda_models:
            if api_model['foreign_id'] == mazda_model['foreign_id']:
                available_model = True
        if not available_model:
            logs.warning("Mazda - This model is no longer available - " + api_model['name'] + " " + api_model['year'] + " (" + api_model['foreign_id'] + ")")  # nopep8

    return logs
