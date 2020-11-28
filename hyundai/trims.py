import json
import requests
import sys

from helpers import api_fetch, get_settings


def run():
    response = api_fetch("make/hyundai/models")
    if response.status_code != 200:
        print("Error! Cannot fetch models from API (Status code: " + str(response.status_code) + ")")  # nopep8
        sys.exit()

    response_json = json.loads(response.content)
    api_models = response_json['models']

    # Fetch the Trims
    content_no_trim_models = ""

    for model in api_models:
        print("Fetching trims of " + model['name'] + " " + model['year'])

        # Fetch trims from the API
        trims_url = "make/hyundai/model/" + model['slug'] + "/trims"
        response = api_fetch(trims_url)
        if response.status_code != 200:
            print("Error! Cannot fetch trims of " + model['slug'] + " from API (Status code: " + str(response.status_code) + ")")  # nopep8
            sys.exit()

        response_json = json.loads(response.content)
        api_trims = response_json['trims']

        # Fetch trims from Hyundai Canada
        model_url = "https://www.hyundaicanada.com/fr/hacc/service/showroom/GetShowroomsModelTrimsJson?modelid={" + model['foreign_id'] + "}&prov=QC&lang=fr"  # nopep8

        hyundai_trims = []
        response = requests.get(model_url)
        if response.status_code == 200:
            hyundai_json = json.loads(response.content)
            if "trims" in hyundai_json:
                for hyundai_trim in hyundai_json['trims']:
                    trim = {
                        "Name": hyundai_trim['trimName'],
                        "Nice name": hyundai_trim['trimName_Fr'],
                        "Foreign ID": hyundai_trim['trimId'],
                    }
                    hyundai_trims.append(trim)

        if len(hyundai_trims) == 0:
            content_no_trim_models += "Name: " + model['name'] + "\n"
            content_no_trim_models += "Year: " + model['year'] + "\n"
            content_no_trim_models += "Foreign ID: " + model['foreign_id'] + "\n"  # nopep8
            content_no_trim_models += "No trims found in Hyundai Canada\n"
            content_no_trim_models += "------------------------------------------------" + "\n"  # nopep8

    if content_no_trim_models != "":
        content_no_trim_models = "No Trims found for those models\n\n" + content_no_trim_models  # nopep8

    return content_no_trim_models
