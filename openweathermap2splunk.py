# -*- coding: utf-8 -*-
import logging
import logging.config
import requests
import time

def get_current_weather(endpoint, apikey, location):
    query = {'q': location, 'appid': apikey}
    res = requests.get(endpoint, params=query)
    res.raise_for_status()
    return res.json()

def kelvin2celsius(deg):
    return deg - 273.15

def post_splunk(url, token, data, index=None):
    localtime = time.localtime()
    localtime_epoch = time.mktime(localtime)
    timestamp = data["dt"]
    payload = []
    for k, v in {
        "temperature": kelvin2celsius(data["main"]["temp"]),
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind.speed": data["wind"]["speed"],
        "wind.deg": data["wind"]["deg"],
        "clouds": data["clouds"]["all"],
        "visibility": data["visibility"],
    }.items():
        payload.append({
            "time": timestamp,
            "event": "metric",
            "source": "openweathermap",
            "host": "openweathermap",
            "index": index,
            "fields": {"metric_name": k, "_value": v},
        })

    headers = {'Authorization': 'Splunk {}'.format(token)}
    res = requests.post(url=url, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()

def main(conf):
    data = get_current_weather(
        endpoint=conf.get('openweathermap', 'url'),
        apikey=conf.get('openweathermap', 'apikey'),
        location=conf.get('openweathermap', 'location'))

    result = post_splunk(
        url=conf.get('splunk', 'url'),
        token=conf.get('splunk', 'token'),
        data=data,
        index=conf.get('splunk', 'metric_index'))

if __name__ == '__main__':
    from argparse import ArgumentParser
    from six.moves.configparser import ConfigParser
    parser = ArgumentParser()
    parser.add_argument('-c', dest='conf', default='openweathermap2splunk.conf')
    args = parser.parse_args()

    conf = ConfigParser()
    conf.read(args.conf)
    main(conf)

