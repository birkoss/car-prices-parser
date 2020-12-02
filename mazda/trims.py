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

    # API - Fetch the trims
    for model in api_models:
        logs.debug("API - Fetching trims of " + model['name'] + " " + model['year'])  # nopep8
        trims_url = "model/" + model['id'] + "/trims"
        response = api_get(trims_url)
        if response.status_code != 200:
            logs.error("API - Cannot fetch trims of " + model['slug'] + " - Status code: " + str(response.status_code))  # nopep8
            return logs
        response_json = json.loads(response.content)
        model['trims'] = response_json['trims']

    # Mazda - Fetch the models
    logs.debug("Mazda - Fetching models and trims")
    response = requests.get("https://www.mazda.ca/common/apps/assets/json/step1/qc.json?v=1547651328198")  # nopep8
    if response.status_code != 200:
        logs.error("Mazda - Cannot fetch models")
        return logs
    mazda_json = json.loads(response.content)

    # Mazda - Reformat models and trims
    mazda_models = []
    for single_category in mazda_json['categories']:
        for single_model in single_category['carline']:
            for single_year in single_model['modelYear']:
                model = {
                    "name": single_model['carline'][0].upper() + single_model['carline'][1:].lower(),  # nopep8
                    "year": str(single_year['year']),
                    "foreign_id": single_model['carline'] + " " + str(single_year['year']),  # nopep8
                    "trims": []
                }

                for single_trim in single_year['trim']:
                    trim = {
                        "name": html.unescape(single_trim['trim']) + " " + html.unescape(single_trim['transmission']['fr']).strip(),  # nopep8
                        "nice_name": "",
                        "foreign_id": single_trim['modelCode']
                    }
                    if single_trim['bodystyle']:
                        trim['name'] += " - " + html.unescape(single_trim['bodystyle']).strip()  # nopep8
                    model['trims'].append(trim)

                mazda_models.append(model)

    # Mazda - Validate models
    if len(mazda_models) == 0:
        logs.error("Mazda - No models founds")
        return logs

    # Validate each Mazda models
    for mazda_model in mazda_models:
        for api_model in api_models:
            if mazda_model['foreign_id'] == api_model['foreign_id']:
                # Validate each Mazda trims
                for mazda_trim in mazda_model['trims']:
                    existing_trim = False
                    for api_trim in api_model['trims']:
                        if api_trim['foreign_id'] == mazda_trim['foreign_id']:  # nopep8
                            existing_trim = True
                    if not existing_trim:
                        response = api_post("model/" + api_model['id'] + "/trims", {  # nopep8
                            "name": mazda_trim['name'],
                            "nice_name": mazda_trim['nice_name'],
                            "foreign_id": mazda_trim['foreign_id'],
                        })
                        if response.status_code == 200:
                            logs.debug("API - Creating - " + api_model['name'] + " " + api_model['year'] + " " + mazda_trim['name'])  # nopep8
                        else:
                            logs.error("API - Cannot create trim - " + api_model['name'] + " " + api_model['year'] + " " + mazda_trim['name'])  # nopep8

    # Warn about the API models not available anymore
    for api_model in api_models:
        # Warn about the API models not available anymore
        for api_trim in api_model['trims']:
            available_trim = False
            for mazda_model in mazda_models:
                for mazda_trim in mazda_model['trims']:
                    if api_trim['foreign_id'] == mazda_trim['foreign_id']:
                        available_trim = True
            if not available_trim:
                logs.warning("Mazda - This trim is no longer available - " + api_model['name'] + " " + api_model['year'] + " " + api_trim['nice_name'] + " (" + api_trim['foreign_id'] + ")")  # nopep8

    return logs
