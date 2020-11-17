#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#xxx

import requests
import os
import sys
import json
import re
from typing import NamedTuple
from influxdb import InfluxDBClient
import datetime
import time
import logging
import credential
#login(credential.username, credential.password)

logger = logging.getLogger(__name__)
ville = "cappelle-la-grande"
myapi = "xxx"

LOGIN_URL = "https://www.rika-firenet.com/web/login"
INFLUXDB_ADDRESS = 'xxx.duckdns.org'
INFLUXDB_USER = credential.influxdb_user
INFLUXDB_PASSWORD = credential.influxdb_password
INFLUXDB_DATABASE = 'xxx_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
location = "salon"

class RikaData(NamedTuple):
    location: str
    measurement: str
    value: float

def _MyLittleMeteo():
    #logging.warning('Watch out!')  # will print a message to the console
    #logging.debug('Watch out!')  # print a message to the console
    #logging.info('nothing')  # will not print anything

    print('start_MyLittleMeteo')  # will not print anything
    url_weather = "http://api.openweathermap.org/data/2.5/weather?q="+ville+"&APPID="+myapi
    r_weather = requests.get(url_weather)
    dataW = r_weather.json()
    #print(dataW)
    print("my little meteo à " + ville)
    eTemperature = dataW['main']['temp']
    #print("La temperature moyenne est de {0:.1f} degres Celsius ".format(eTemperature-273.15))
    eHumidite = dataW['main']['humidity']
    #print("Taux d'humidite de {}".format(eHumidite) + "%")

    value = round((eTemperature-273.15),2)
    measurement = "eTemperature"
    send_payload([create_payload(location, measurement, value)])

    value = eHumidite
    measurement = "eHumidite"
    send_payload([create_payload(location, measurement, value)])
    logging.debug('finish_MyLittleMeteo')  # will not print anything

def create_payload(loc, mea, val):
    return {
        'measurement': mea,
        'tags': {
            'location': loc
        },
        'fields': {
            'value': val
        }
    }

def send_payload(payload):
    influxdb_client.write_points(payload)
    print('sending payload' +str(payload))  # will not print anything

def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
        print('create database')  # will not print anything
    influxdb_client.switch_database(INFLUXDB_DATABASE)
    print('use this database : ' +str(INFLUXDB_DATABASE))  # will not print anything

def main():
    print('main start')  # will not print anything
    _init_influxdb_database()
    _MyLittleMeteo()

    # Fill in your details here to be posted to the login form.
    payload = {
        'email': credential.api_email,
        'password': credential.api_password
    }

    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=payload)

        # An authorised request.
        rika_dict = s.get('https://www.rika-firenet.com/api/client/xxx/status')

        usuable_dict = rika_dict.json()
        controls_dict = (usuable_dict["controls"])
        sensors_dict = (usuable_dict["sensors"])
        stoveFeatures = (usuable_dict["stoveFeatures"])
        #print(sensors_dict)
        print('dict acquired')  # will not print anything
        #location = "salon"

        measurements = [
            "inputRoomTemperature",
            #"inputFlameTemperature",
            #"parameterRuntimePellets",
            #"parameterFeedRateTotal",
            #"parameterFeedfRateService"
        ]

        payload = [create_payload(location, f"{measurement}_value", float(sensors_dict[measurement])) for measurement in measurements]

        send_payload(payload)

        measurements = [
            #"inputRoomTemperature",
            "inputFlameTemperature",
            "parameterRuntimePellets",
            "parameterFeedRateTotal",
            "parameterFeedRateService"
        ]

        payload = [create_payload(location, f"{measurement}_value", sensors_dict[measurement]) for measurement in measurements]
        #payload = [create_payload(location, f"{measurement}_value", controls_dict[measurement]) for measurement in measurements]
        send_payload(payload)

        """
        print('Flame    Temperature value : ' + str (inputFlameTemperature_value))
        print('Runtime  Pellets value : ' + str (parameterRuntimePellets_value))
        print('FeedRate Total value : ' + str (parameterFeedRateTotal_value))
        print('FeedRate Service value : ' + str (parameterFeedRateService_value))
        """

        measurements = ["onOff", "operatingMode", "heatingPower", "targetTemperature", "ecoMode"]

        payload = [create_payload(location, f"{measurement}_value", controls_dict[measurement]) for measurement in measurements]

        send_payload(payload)

        """
        print ('onOff value : ' + str (onOff_value))
        print ('operatingMode value : ' + str (operatingMode_value))
        print ('heatingPower value : ' + str (heatingPower_value))
        print ('targetTemperature value : ' + str (targetTemperature_value))
        print ('ecoMode value : ' + str (ecoMode_value))
        """
        #if rika_data is not None:
        #    send_rika_data_to_influxdb(rika_data)
        print('payloads sended')  # will not print anything
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
