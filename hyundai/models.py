import json
import requests
import sys

from helpers import api_get, api_post
from logs import Logs


def run():
    logs = Logs()

    # API - Fetch the models
    models_url = "make/hyundai/models"
    logs.debug("API - Fetching models")
    response = api_get(models_url)
    if response.status_code != 200:
        logs.error("API - Cannot fetch models - Status code: " + response.status_code)  # nopep8
        return logs
    api_json = json.loads(response.content)
    api_models = api_json['models']

    # Hyundai - Fetch the models
    response = requests.get("https://www.hyundaicanada.com/fr/hacc/service/showroom/GetShowroomsModelJson?lang=fr")  # nopep8
    if response.status_code != 200:
        logs.error("Hyundai - Cannot fetch models")
        return logs

    # Hyundai - Validate models
    hyundai_json = json.loads(response.content)
    if "models" not in hyundai_json:
        logs.error("Hyundai - No models node found in the JSON")
        return logs

    # Hyundai - Reformat models
    # - An array for each models containing a nested array for each years
    hyundai_models = []
    for models in hyundai_json['models']:
        for single_model in models:
            model = {
                # Name are uppercased
                "name": single_model['vehicleName_Fr'][0].upper() + single_model['vehicleName_Fr'][1:].lower(),  # nopep8
                "year": single_model['vehicleYear'],
                # Hyundai have { and } around the foreign_id
                # - [1:-1] to remove it
                "foreign_id": single_model['modelId'][1:-1],
            }
            hyundai_models.append(model)

    # Create new model
    for hyundai_model in hyundai_models:
        existing_model = False
        for api_model in api_models:
            if api_model['foreign_id'] == hyundai_model['foreign_id']:
                existing_model = True
        if not existing_model:
            response = api_post(models_url, {
                "name": hyundai_model['name'],
                "year": hyundai_model['year'],
                "foreign_id": hyundai_model['foreign_id'],
            })
            if response.status_code == 200:
                logs.debug("API - Creating - " + hyundai_model['name'] + " " + hyundai_model['year'])  # nopep8
            else:
                logs.error("API - Cannot create model - " + hyundai_model['name'] + " " + hyundai_model['year'])  # nopep8

    # Warn about the API models not available anymore
    for api_model in api_models:
        available_model = False
        for hyundai_model in hyundai_models:
            if api_model['foreign_id'] == hyundai_model['foreign_id']:
                available_model = True
        if not available_model:
            logs.warning("Hyundai - This model is no longer available - " + api_model['name'] + " " + api_model['year'] + " (" + api_model['foreign_id'] + ")")  # nopep8

    return logs
