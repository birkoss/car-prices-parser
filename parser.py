import sys

from hyundai.models import run as hyundai_models
from hyundai.trims import run as hyundai_trims
from mazda.models import run as mazda_models
from mazda.trims import run as mazda_trims

switcher = {
    "hyundai_models": hyundai_models,
    "hyundai_trims": hyundai_trims,
    "mazda_models": mazda_models,
    "mazda_trims": mazda_trims,
}

make = ""
if len(sys.argv) > 1:
    make = sys.argv[1]

function = ""
if len(sys.argv) > 2:
    function = sys.argv[2]

if make == "" or function == "":
    print("Must specific a brand and a function")
    sys.exit()

# Let's do it
function_name = switcher.get(make+"_"+function, lambda: "Invalid function")

logs = function_name()

print(logs)
