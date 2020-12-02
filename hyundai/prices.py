import json
import requests
import sys

from helpers import api_get, api_post, create_md5, format_price
from logs import Logs


def run():
    logs = Logs()

    # API - Fetch the trims
    logs.debug("API - Fetching trims\n")
    response = api_get("make/hyundai/trims")
    if response.status_code != 200:
        logs.error("API - Cannot fetch trims - Status code: " + str(response.status_code))  # nopep8
        return logs
    response_json = json.loads(response.content)
    api_trims = response_json['trims']

    for api_trim in api_trims:
        trim_fullname = api_trim['model']['name'] + " " + api_trim['model']['year'] + " " + api_trim['nice_name']  # nopep8
        logs.debug("API - Fetching prices - " + trim_fullname)  # nopep8

        response = requests.get("https://www.hyundaicanada.com/fr/hacc/service/pricemaster/model/trim/alloptions?trimId=" + api_trim['foreign_id'] + "&prov=QC&lang=fr")  # nopep8
        if response.status_code != 200:
            logs.warning("Hyundai - Cannot fetch price - " + trim_fullname)
            continue

        hyundai_prices = json.loads(response.content)

        # Get the rebates incentives for each price type per term
        rebates = {"finance": {}, "lease": {}, "cash": {}}
        for rebate in hyundai_prices['rebates']:
            if rebate['rebateSelected']:
                for rebateType in rebate['rebateTypes']:
                    for rebateOption in rebateType['rebateOptions']:
                        if rebateOption['term'] not in rebates[rebateType['type'].lower()]:  # nopep8
                            rebates[rebateType['type'].lower()][rebateOption['term']] = 0  # nopep8

                        # Add the rebate amount (WITHOUT TAXES !!!!!!!) Taxes : QC + CA = 1.14975    # nopep8
                        rebates[rebateType['type'].lower()][rebateOption['term']] += (rebateOption['amount'] / 1.14975)  # nopep8

        # Get the taxes total
        taxes = 0
        for taxe in hyundai_prices['taxesOrLevies']:
            taxes += taxe['amount']

        # Prepare the prices JSON
        prices = {
            "cash": {
                "msrp": format_price(hyundai_prices['msrp']),
                "delivery": format_price(hyundai_prices['delivery']),
                "taxe": format_price(taxes),
                "incentive": "0"
            },
            "finance": [],
            "lease": []
        }

        # Get all purchase options
        for purchaseOption in hyundai_prices['purchaseOptions']:
            price_type = purchaseOption['type'].lower()
            if price_type == "finance" or price_type == "lease" or price_type == "cash":  # nopep8
                for option in purchaseOption['options']:
                    term = option['term']
                    if price_type == "finance":
                        term = 0

                    # Apply the incentive for this term
                    if term in rebates[price_type]:
                        if rebates[price_type][term] > 0:
                            option['incentive'] = rebates[price_type][term]  # nopep8
        
                    if price_type == "cash":
                        prices['cash']['incentive'] = format_price(option['incentive'])  # nopep8
                    else:
                        price = {
                            "incentive": format_price(option['incentive']),
                            "term": format_price(option['term']),
                            "rate": format_price(option['rate']),
                        }

                        # Lease needs a residual amount
                        if price_type == "lease":
                            price["residual"] = format_price(option['residualAmount16k'] / hyundai_prices['msrp'])  # nopep8

                        prices[price_type].append(price)

        for price_type in prices:
            md5 = create_md5(json.dumps(prices[price_type]))

            price_url = "trim/" + api_trim['id'] + "/price/" + price_type  # nopep8
            logs.debug("API - Pushing price (" + price_type + ") - " + trim_fullname)  # nopep8
            response = api_post(price_url, {
                "hash": create_md5(json.dumps(prices[price_type])),
                "data": json.dumps(prices[price_type])
            })
            if response.status_code != 200:
                logs.error("API - Cannot push price (" + price_type + ") - Status code: " + str(response.status_code))  # nopep8
                return logs
            else:
                api_json = json.loads(response.content)
                logs.debug("API - Response: " + api_json['message'])

    return logs
