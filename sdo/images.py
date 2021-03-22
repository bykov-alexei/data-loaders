#!/usr/bin/python3
import argparse
from datetime import datetime, timedelta
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('--start-date', type=str, required=True)
parser.add_argument('--end-date', type=str, default=datetime.today().strftime('%Y-%m-%d'))
parser.add_argument('--telescope', type=str, choices=['aia_0171'], required=True)
parser.add_argument('--resolution', type=str, choices=['512', '1024', '2048', '4096'], required=True)
parser.add_argument('--cadence', type=int, default=1)
parser.add_argument('--folder', type=pathlib.Path, required=True)
args = parser.parse_args()


import os
import requests
import time
import urllib
from urllib.request import urlretrieve


class mRequests:
    
    @staticmethod
    def get(*args, **kwargs):
        for i in range(5):
            try:
                response = requests.get(*args, **kwargs)
                return response
            except requests.exceptions.ConnectionError as e:
                print('Connection aborted. Sleeping for 5 seconds')
                time.sleep(5)
        
    @staticmethod
    def post(*args, **kwargs):
        for i in range(5):
            try:
                response = requests.post(*args, **kwargs)
                return response
            except requests.exceptions.ConnectionError as e:
                print('Connection aborted. Sleeping for 5 seconds')
                time.sleep(5)

def make_request(start_date: str, end_date: str, telescope: str, resolution: str, cadence: int) -> str:
    data = {
    'm': 'init',
    'start': start_date,
    'end': end_date,
    'telescope': telescope,
    'display': 'archive',
    'resolution': resolution,
    'cadence': str(cadence)
    }

    response = mRequests.post('https://sdo.gsfc.nasa.gov/data/aiahmi/browse/init.php', data=data)
    assert response.ok
    try:
        token = response.text.split('var myhash = ')[1].split('\'')[1]
    except IndexError:
        return None
    return token


def check_status(token: str, start_date: str, end_date: str):
    params = (
        ('hash', token),
        ('display', 'checkstatus'),
        ('m', 'json'),
        ('t', 'archive'),
        ('start', start_date + ' 00:00:00'),
        ('end', end_date + ' 23:59:59'),
    )
    
    response = mRequests.get('https://sdo.gsfc.nasa.gov/data/aiahmi/browse/init.php', params=params)
    return response


delta = timedelta(days=3)
start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
while start_date < end_date - delta:
    s_date = start_date.strftime('%Y-%m-%d')
    e_date = (start_date + delta).strftime('%Y-%m-%d')
    
    token = make_request(
        start_date=s_date, 
        end_date=e_date, 
        telescope=args.telescope,
        resolution=args.resolution,
        cadence=args.cadence)
    if token:
        while True:
            response = check_status(token, args.start_date, args.end_date)
            if response.text:
                data = response.json()
                if data['0']['locked'] == '1':
                    url = 'https://sdo.gsfc.nasa.gov/assets' + data['0']['filepath'] + data['0']['filename']
                    os.makedirs(args.folder, exist_ok=True)
                    while True:
                        try:
                            urlretrieve(url, os.path.join(args.folder, data['0']['filename']))
                            break
                        except urllib.error.ContentTooShortError:
                            continue
                    break
            time.sleep(2)
    start_date = start_date + delta
    
