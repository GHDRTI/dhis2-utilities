import argparse
import sys
from os.path import join, dirname
from dotenv import load_dotenv
import requests
import os
import pandas as pd
import numpy as np
import json

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--uid",
                    help="this uid of admin0 in the destination DHIS2 system where you are importing org units from.")
parser.add_argument("-n", "--name", help='this name of the admin0 in geoconnect you want to pull in org units from')
parser.add_argument("-a", "--attribute", help='this is the geoconnect attribute uid in DHIS2')
args = parser.parse_args()

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

ADMIN0_UID = str(args.uid)
ADMIN0_NAME = str(args.name)
ATTRIBUTE_UID = str(args.attribute)
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
    parent_id = {"id": ADMIN0_UID}

    row = {"name": region,
           "shortName": region,
           "openingDate": "1970-01-01T00:00:00.000",
           "id": region_uid,
           "parent": parent_id}
    export.append(row)
    org_counter = org_counter + 1

    admin1_df = orgunits[orgunits['admin1'] == region]
    admin1_df = admin1_df.loc[admin1_df['admin2'].notnull()]
    districts = np.unique(admin1_df[['admin2']].values)

    # loop through each of the admin2s for each admin1

    for district in districts:

        district_uid = "ORG" + '%08d' % org_counter
        parent_id = {"id": region_uid}
        row = {"name": district,
               "shortName": district,
               "openingDate" : "1970-01-01T00:00:00.000",
               "id": district_uid,
               "parent": parent_id}
        export.append(row)
        org_counter = org_counter + 1

        # loop through each of the admin3s for each admin2
        admin2_df = orgunits[orgunits['admin2'] == district]

        admin2_df = admin2_df.loc[admin2_df['admin3'].notnull()]
        subdistricts = np.unique(admin2_df[['admin3']].values)

        for index, row in admin2_df.iterrows():

            attr_value = {"id": ATTRIBUTE_UID}
            attribute_data = {"value": row['geoconnect_id'], "attribute": attr_value}
            attributeValues = [attribute_data]

            subdistrict_uid = "ORG" + '%08d' % org_counter

            parent_id = {"id": district_uid}

            row = {"name": row['admin3'],
                   "shortName": row['admin3'],
                   "openingDate": "1970-01-01T00:00:00.000",
                   "id": subdistrict_uid,
                   "parent": parent_id,
                   "attributeValues": attributeValues}

            export.append(row)
            org_counter = org_counter + 1


orgunits = {"organisationUnits": export}
jstr = json.dumps(orgunits, ensure_ascii=False, indent=4)
print(jstr)