#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#cf1cc9f567a1427aa85f4cc553727ff1

import requests
import os
import sys
import json
import re
from typing import NamedTuple
from influxdb import InfluxDBClient
import datetime
import time

import credential
#login(credential.username, credential.password)

ville = "cappelle-la-grande"
myapi = "cf1cc9f567a1427aa85f4cc553727ff1"


LOGIN_URL = "https://www.rika-firenet.com/web/login"
INFLUXDB_ADDRESS = 'picollo.duckdns.org'
INFLUXDB_USER = credential.influxdb_user
INFLUXDB_PASSWORD = credential.influxdb_password
INFLUXDB_DATABASE = 'rika_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
location = "salon"

class RikaData(NamedTuple):
    location: str
    measurement: str
    value: float

def _MyLittleMeteo():
    url_weather = "http://api.openweathermap.org/data/2.5/weather?q="+ville+"&APPID="+myapi
    r_weather = requests.get(url_weather)
    data = r_weather.json()
    #print(data)
    print("my little meteo à " + ville)
    eTemperature = data['main']['temp']
    #print("La temperature moyenne est de {0:.1f} degres Celsius ".format(eTemperature-273.15))
    eHumidite = data['main']['humidity']
    #print("Taux d'humidite de {}".format(eHumidite) + "%")

    value = round((eTemperature-273.15),2)
    eTemperature = value
    measurement = "eTemperature"
    _send_rika_data_to_influxdb(location, measurement, value)

    value = eHumidite
    measurement = "eHumidite"
    _send_rika_data_to_influxdb(location, measurement, value)

def _send_rika_data_to_influxdb(loc, mea, val):
    json_body = [
                    {
                        'measurement': mea,
                        'tags': {
                            'location': loc
                        },
                        'fields': {
                            'value': val
                        }
                    }
    ]
    influxdb_client.write_points(json_body)
    print(json_body)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)



def main():

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
        rika_dict = s.get('https://www.rika-firenet.com/api/client/93933394/status')
        doublequote_dict = json.dumps(rika_dict.json())
        print(doublequote_dict)
        #print()

        usuable_dict = json.loads(doublequote_dict)
        controls_dict = (usuable_dict["controls"])
        sensors_dict = (usuable_dict["sensors"])
        stoveFeatures = (usuable_dict["stoveFeatures"])
        #print(sensors_dict)

        #location = "salon"


        inputRoomTemperature_value = float(sensors_dict["inputRoomTemperature"])
        value = inputRoomTemperature_value
        measurement = "inputRoomTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        inputFlameTemperature_value = (sensors_dict["inputFlameTemperature"])
        value = inputFlameTemperature_value
        measurement = "inputFlameTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        parameterRuntimePellets_value = (sensors_dict["parameterRuntimePellets"])
        value = parameterRuntimePellets_value
        measurement = "parameterRuntimePellets_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        parameterFeedRateTotal_value = (sensors_dict["parameterFeedRateTotal"])
        value = parameterFeedRateTotal_value
        measurement = "parameterFeedRateTotal_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        parameterFeedRateService_value = (sensors_dict["parameterFeedRateService"])
        value = parameterFeedRateService_value
        measurement = "parameterFeedRateService_value"
        _send_rika_data_to_influxdb(location, measurement, value)
        """
        print('Flame    Temperature value : ' + str (inputFlameTemperature_value))
        print('Runtime  Pellets value : ' + str (parameterRuntimePellets_value))
        print('FeedRate Total value : ' + str (parameterFeedRateTotal_value))
        print('FeedRate Service value : ' + str (parameterFeedRateService_value))
        """


        onOff_value = (controls_dict["onOff"])
        value = onOff_value
        measurement = "ponOff_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        operatingMode_value = (controls_dict["operatingMode"])
        value = operatingMode_value
        measurement = "operatingMode_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        heatingPower_value = (controls_dict["heatingPower"])
        value = heatingPower_value
        measurement = "heatingPower_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        targetTemperature_value = (controls_dict["targetTemperature"])
        value = targetTemperature_value
        measurement = "targetTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)

        ecoMode_value = (controls_dict["ecoMode"])
        value = ecoMode_value
        measurement = "ecoMode_value"
        _send_rika_data_to_influxdb(location, measurement, value)
        """
        print ('onOff value : ' + str (onOff_value))
        print ('operatingMode value : ' + str (operatingMode_value))
        print ('heatingPower value : ' + str (heatingPower_value))
        print ('targetTemperature value : ' + str (targetTemperature_value))
        print ('ecoMode value : ' + str (ecoMode_value))
        """
        #if rika_data is not None:
        #    send_rika_data_to_influxdb(rika_data)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
