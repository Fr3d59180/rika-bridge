#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#

## recuperer T°& H% exterieur
## T° ambiante, flamme, mode, consigne de T°
## conso et utilisation
## toute les 5mins(crontab)

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
myapi = ""


LOGIN_URL = "https://www.rika-firenet.com/web/login"
INFLUXDB_ADDRESS = 'picollo.duckdns.org'
INFLUXDB_USER = credential.influxdb_user
INFLUXDB_PASSWORD = credential.influxdb_password
INFLUXDB_DATABASE = 'Ambiente-rika_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
location = ""

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

    #externe temp
    value = round((eTemperature-273.15),2)
    eTemperature = value
    measurement = "ext_Temperature"
    _send_rika_data_to_influxdb(location, measurement, value)
    #externe humidité
    value = eHumidite
    measurement = "ext_Humidite"
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
    ##print(json_body)


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
        rika_dict = s.get('https://www.rika-firenet.com/api/client/xxx/status')
        doublequote_dict = json.dumps(rika_dict.json())
        #print(doublequote_dict)
        #print()

        usuable_dict = json.loads(doublequote_dict)
        controls_dict = (usuable_dict["controls"])
        sensors_dict = (usuable_dict["sensors"])
        stoveFeatures = (usuable_dict["stoveFeatures"])
        print(" controls ")
        print(controls_dict)
        print("")

        print(" sensors ")
        print(sensors_dict)
        print("")

        print(" features ")
        print(stoveFeatures)
        print("")

        """
        #thermostat
        inputRoomTemperature_value = float(sensors_dict["inputRoomTemperature"])
        value = inputRoomTemperature_value
        measurement = "inputRoomTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)
	#flamme
        inputFlameTemperature_value = (sensors_dict["inputFlameTemperature"])
        value = inputFlameTemperature_value
        measurement = "inputFlameTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)
	#utilisation
        parameterRuntimePellets_value = (sensors_dict["parameterRuntimePellets"])
        value = parameterRuntimePellets_value
        measurement = "parameterRuntimePellets_value"
        _send_rika_data_to_influxdb(location, measurement, value)
	#conso
        parameterFeedRateTotal_value = (sensors_dict["parameterFeedRateTotal"])
        value = parameterFeedRateTotal_value
        measurement = "parameterFeedRateTotal_value"
        _send_rika_data_to_influxdb(location, measurement, value)
	#mode 0=auto, 1=manu, 2=conf
        operatingMode_value = (controls_dict["operatingMode"])
        value = operatingMode_value
        measurement = "operatingMode_value"
        _send_rika_data_to_influxdb(location, measurement, value)
	### consigne
        targetTemperature_value = (controls_dict["targetTemperature"])
        value = targetTemperature_value
        measurement = "targetTemperature_value"
        _send_rika_data_to_influxdb(location, measurement, value)
        """

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

#'operatingMode_value', 'tags': {'location': 'salon'}, 'fields': {'value': 0}}]
#0 manual, 1 automatique, 2 confort

#'ponOff_value', 'tags': {'location': 'salon'}, 'fields': {'value': False}}]
#false eteint, true allumé

#'targetTemperature_value', 'tags': {'location': 'salon'}, 'fields': {'value': '20'}}]
# consigne de T° pour le mode confort
