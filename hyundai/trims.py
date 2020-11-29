import json
import requests
import sys

from helpers import api_get, api_post
from logs import Logs


def run():
    logs = Logs()

    # API - Fetch the models
    logs.debug("API - Fetching models\n")
    response = api_get("make/hyundai/models")
    if response.status_code != 200:
        logs.error("API - Cannot fetch models - Status code: " + str(response.status_code))  # nopep8
        return logs
    response_json = json.loads(response.content)
    api_models = response_json['models']

    for model in api_models:
        # API - Fetch the trims
        logs.debug("API - Fetching trims of " + model['name'] + " " + model['year'])  # nopep8
        trims_url = "make/hyundai/model/" + model['slug'] + "/trims"
        response = api_get(trims_url)
        if response.status_code != 200:
            logs.error("API - Cannot fetch trims of " + model['slug'] + " - Status code: " + str(response.status_code))  # nopep8
            return logs
        response_json = json.loads(response.content)
        api_trims = response_json['trims']

        # Hyundai - Fetch the trims
        model_url = "https://www.hyundaicanada.com/fr/hacc/service/showroom/GetShowroomsModelTrimsJson?modelid={" + model['foreign_id'] + "}&prov=QC&lang=fr"  # nopep8
        hyundai_trims = []
        logs.debug("Hyundai - Fetching trims of " + model['name'] + " " + model['year'])  # nopep8
        response = requests.get(model_url)
        if response.status_code == 200:
            hyundai_json = json.loads(response.content)
            if "trims" in hyundai_json:
                for hyundai_trim in hyundai_json['trims']:
                    trim = {
                        "name": hyundai_trim['trimName'],
                        "nice_name": hyundai_trim['trimName_Fr'],
                        "foreign_id": hyundai_trim['trimId'],
                    }
                    hyundai_trims.append(trim)

        # Hyundai - Validate the trims
        if len(hyundai_trims) == 0:
            logs.warning("Hyundai - No trims found for " + model['name'] + " " + model['year'] + " (" + model['foreign_id'] + ")")  # nopep8

        # Hyundai - Create new trims
        for hyundai_trim in hyundai_trims:
            existing_trim = False
            for api_trim in api_trims:
                if api_trim['foreign_id'] == hyundai_trim['foreign_id']:
                    existing_trim = True
            if not existing_trim:
                response = api_post(trims_url, {
                    "name": hyundai_trim['name'],
                    "nice_name": hyundai_trim['nice_name'],
                    "foreign_id": hyundai_trim['foreign_id'],
                })
                if response.status_code == 200:
                    logs.debug("API - Creating - " + model['name'] + " " + model['year'] + " " + hyundai_trim['nice_name'])  # nopep8
                else:
                    logs.error("API - Cannot create trim - " + model['name'] + " " + model['year'] + " " + hyundai_model['nice_name'])  # nopep8

        # Warn about the API models not available anymore
        for api_trim in api_trims:
            available_trim = False
            for hyundai_trim in hyundai_trims:
                if api_trim['foreign_id'] == hyundai_trim['foreign_id']:
                    available_trim = True
            if not available_trim:
                logs.warning("Hyundai - This trim is no longer available - " + model['name'] + " " + model['year'] + " " + api_trim['nice_name'] + " (" + api_trim['foreign_id'] + ")")  # nopep8

    return logs
