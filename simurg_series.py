#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--site', dest='site', type=str)
parser.add_argument('--mail', dest='mail', type=str)
parser.add_argument('--n-queries', dest='n_queries', type=int, default=3)
parser.add_argument('--start-date', dest='start_date', type=str, default='1990-01-01')
parser.add_argument('--folder', dest='folder', type=str, default='data')
args = parser.parse_args()

import requests
import json
import os
from datetime import datetime, timedelta
from urllib.request import urlretrieve

def get_stations():
    data = {
        "method": "get_site",
        "args": [],
    }
    response = requests.post('https://simurg.iszf.irk.ru/api', data=json.dumps(data))
    assert response.ok
    return response.json()

def create_query(email: str, site: str, begin: datetime, end: datetime):
    data = {
        "method": "create_series",
        "args": {
            "email": email,
            "begin": begin.strftime('%Y-%m-%d %H:%M'),
            "end": end.strftime('%Y-%m-%d %H:%M'),
            "site": site,
            "options": {
                "subsolar": False,
                "mageq": False
            },
            "flags": {
                "only_available": False,
                "create_movie": False,
                "create_plots": False
            }
        }
    }
    response = requests.post('https://simurg.iszf.irk.ru/api', data=json.dumps(data))
    assert response.ok
    return response

def get_queries(email: str): 
    data = {
        'method': 'check',
        'args': {
            'email': 'mail@bykov-alexei.ru'
        }
    }
    response = requests.post('https://simurg.iszf.irk.ru/api', data=json.dumps(data))
    assert response.ok
    return response.json()

def delete_query(id: str):
    data = {
        'method': 'delete',
        'args': {
            'id': id,
        }
    }
    response = requests.post('https://simurg.iszf.irk.ru/api', data=json.dumps(data))
    assert response.ok
    return response

def download_data(query: dict, directory: str): 
    assert query['status'] == 'done'
    file_name = query['paths']['data'].split('/')[-1]
    url = "https://simurg.iszf.irk.ru/tecs/"+query['paths']['data']
    os.mkdirs(directory, exists_ok=True)
    urlretrieve(url, os.path.join(directory, file_name))
    return None

site = args.site
mail = args.mail
n_queries = args.n_queries
running = 0

stations = get_stations()
queries = get_queries(mail)
for query in queries:
    delete_query(query['id'])
    
current = datetime.strptime(args.start_date, '%Y-%m-%d')

while current < datetime.now() - timedelta(days=3):
    if running < n_queries:
        create_query(mail, site, current, current + timedelta(days=3))
        print('Query created')
        current = current + timedelta(days=3)
        running += 1
    queries = get_queries(mail)
    for query in queries:
        if query['status'] == 'failed':
            print('Query failed. Deleting ...')
            delete_query(query['id'])
            print('Deleted')
            running -= 1
        if query['status'] == 'done':
            print('Query done. Downloading...')
            download_files(query, os.path.join(args.folder, args.site))
            print('Downloaded. Deleting...')
            delete_query(query['id'])
            print('Deleted')
            running -= 1
            
while running != 0:
    for query in queries:
        if query['status'] == 'failed':
            delete_query(query['id'])
            running -= 1
        if query['status'] == 'done':
            download_files(query, os.path.join(args.folder, args.site))
            running -= 1
