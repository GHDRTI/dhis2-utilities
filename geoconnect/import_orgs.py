import argparse
import sys
from os.path import join, dirname
from dotenv import load_dotenv
import requests
import os
import pandas as pd
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

# Get data from Geoconect API

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
org_counter = 1
export = []
regions = np.unique(orgunits['admin1'].values)
for region in regions:

    region_uid = "ORG" + '%08d' % org_counter
    row = {"name": region, "uid": region_uid, "parent": ADMIN0_UID}
    export.append(row)
    org_counter = org_counter + 1

    admin1_df = orgunits[orgunits['admin1'] == region]
    admin1_df = admin1_df.loc[admin1_df['admin2'].notnull()]
    districts = np.unique(admin1_df[['admin2']].values)

    # loop through each of the admin2s for each admin1

    for district in districts:

        district_uid = "ORG" + '%08d' % org_counter
        row = {"name": district, "uid": district_uid, "parent": region_uid}
        export.append(row)
        org_counter = org_counter + 1

        # loop through each of the admin3s for each admin2
        admin2_df = orgunits[orgunits['admin2'] == district]

        admin2_df = admin2_df.loc[admin2_df['admin3'].notnull()]
        subdistricts = np.unique(admin2_df[['admin3']].values)

        for subdistrict in subdistricts:
            subdistrict_uid = "ORG" + '%08d' % org_counter
            row = {"name": subdistrict, "uid": subdistrict_uid, "parent": district_uid}
            export.append(row)
            org_counter = org_counter + 1

# Export to a CSV like this: name,uid,code,parent
print("name,uid,code,parent")
for n in export:
    print(n['name']+","+n['uid']+",,"+n['parent'])