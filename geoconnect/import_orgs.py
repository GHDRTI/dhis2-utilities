import argparse
import sys
from os.path import join, dirname
from dotenv import load_dotenv
import requests
import os
import pandas as pd
import io
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--uid",
                    help="this uid of admin0 in the destination DHIS2 system where you are importing org units from.")
parser.add_argument("-n", "--name", help='this name of the admin0 in geoconnect you want to pull in org units from')

args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

ADMIN0_UID = str(args.uid)
ADMIN0_NAME = str(args.name)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
API_KEY = os.environ.get("API_KEY")

# Get data from API

s = requests.session()
counter = 1
results = []
while True:
    page = s.get(
        "https://www.geoconnect.org/api/countries?api_key=" + API_KEY + "&admin0=" + ADMIN0_NAME + "&page=" + str(
            counter))

    df = pd.read_json(page.content.decode('utf-8'))

    if len(df.index) == 0:
        break

    results.append(df)
    counter = counter + 1

orgunits = pd.concat(results)



# Build out the org heirarchy for DHIS2

counter = 1
export = []
regions = np.unique(orgunits[['admin1']].values)
for region in regions:
    row = {"name": region, "uid":"ORG"+'%08d' % counter, "parent": ADMIN0_UID}
    export.append(row)
    counter = counter + 1



# Export to a CSV like this: name,uid,code,parent
print("name,uid,code,parent")
for n in export:
    print(n['name']+","+n['uid']+",,"+n['parent'])