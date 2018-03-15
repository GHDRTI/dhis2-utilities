## Generate DHIS2 metadata import file from GeoConnect

This command script generates a CSV file that can be imported into DHIS2 for created orgnization units from[GeoConnect](https://www.geoconnect.org).

### Here is how to use this

* Run `pip freeze -r requirements.txt` to load dependencies
* Specify the api key for in a .env file
* Run python import_orgs.py -u [UID] -n [GEOCONNECT ADMIN NAME]


