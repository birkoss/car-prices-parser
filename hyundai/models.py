import json
import requests
import sys

from helpers import api_fetch, api_post


def run():
    models_url = "make/hyundai/models"

    # Fetch the existing models from the API
    response = api_fetch(models_url)
    if response.status_code != 200:
        print("Error! Cannot fetch models from API (Status code: " + response.status_code + ")")  # nopep8
        sys.exit()

    api_json = json.loads(response.content)
    api_models = api_json['models']

    # Fetch the models from Hyundai
    response = requests.get("https://www.hyundaicanada.com/fr/hacc/service/showroom/GetShowroomsModelJson?lang=fr")  # nopep8
    if response.status_code != 200:
        print("Error! Cannot fetch models from Hyundai Canada")
        sys.exit()

    hyundai_json = json.loads(response.content)
    if "models" not in hyundai_json:
        print("Error! Hyundai Canada JSON changed! No models node found!")
        sys.exit()

    # Hyundai's models are an array for each models and a nested array
    # for the available year in it
    hyundai_models = []
    for models in hyundai_json['models']:
        for single_model in models:
            model = {
                "name": single_model['vehicleName_Fr'][0].upper() + single_model['vehicleName_Fr'][1:].lower(),  # nopep8
                "year": single_model['vehicleYear'],
                # Since hyundai have { and } around the foreign_id
                # [1:-1] to remove it
                "foreign_id": single_model['modelId'][1:-1],
            }

            hyundai_models.append(model)

    # Show the models missing from the API
    # ------------------------------------
    content_new_models = ""
    for hyundai_model in hyundai_models:
        found = False
        for api_model in api_models:
            if api_model['foreign_id'] == hyundai_model['foreign_id']:
                found = True

        if not found:
            response = api_post(models_url, {
                "name": hyundai_model['name'],
                "year": hyundai_model['year'],
                "foreign_id": hyundai_model['foreign_id'],
            })
            if response.status_code == 200:
                print(hyundai_model['name'] + " " + hyundai_model['year'] + " created!")  # nopep8
            else:
                content_new_models += "Error! Cannot create model " + hyundai_model['name'] + " " + hyundai_model['year'] + "!\n"  # nopep8

    if content_new_models != "":
        content_new_models = "New models from Hyundai Canada\n\n" + content_new_models  # nopep8

    # Show the API models not available anymore from Hyundai
    # ------------------------------------------------------
    content_deleted_models = ""
    for api_model in api_models:
        found = False
        for hyundai_model in hyundai_models:
            if api_model['foreign_id'] == hyundai_model['foreign_id']:
                found = True

        if not found:
            content_deleted_models += "Name: " + api_model['name'] + "\n"
            content_deleted_models += "Year: " + api_model['year'] + "\n"
            content_deleted_models += "Foreign ID: " + api_model['foreign_id'] + "\n"  # nopep8
            content_deleted_models += "------------------------------------------------" + "\n"  # nopep8

    if content_deleted_models != "":
        content_deleted_models = "Deleted models from Hyundai Canada\n\n" + content_deleted_models  # nopep8

    return content_new_models + content_deleted_models
