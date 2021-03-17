#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(description='Checks stations validity')
parser.add_argument("stations", help="List of stations", nargs='+', type=str)
args = parser.parse_args()

import requests
import json

def get_stations():
    data = {
        "method": "get_site",
        "args": [],
    }
    response = requests.post('https://simurg.iszf.irk.ru/api', data=json.dumps(data))
    assert response.ok
    return response.json()

stations = get_stations()
for station in args.stations:
    print(station, 'is' if station in stations else 'is NOT', 'in list') 
