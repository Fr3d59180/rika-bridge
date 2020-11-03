#!/usr/bin/env python3
import requests
import os
import sys
import json
import re
from typing import NamedTuple
from influxdb import InfluxDBClient



LOGIN_URL = "https://www.rika-firenet.com/web/login"
INFLUXDB_ADDRESS = 'picollo.duckdns.org'
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'rika_db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
location = "salon"

class RikaData(NamedTuple):
    location: str
    measurement: str
    value: float

def _send_rika_data_to_influxdb(Rika_Data):
    json_body = [
                    {
                        'measurement': RikaData.measurement,
                        'tags': {
                            'location': RikaData.location
                        },
                        'fields': {
                            'value': RikaData.value
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

    # Fill in your details here to be posted to the login form.
    payload = {
        'email': 'fr3d.mobile@gmail.com',
        'password': 'Dj@ng059'
    }

    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=payload)

        # An authorised request.
        rika_dict = s.get('https://www.rika-firenet.com/api/client/93933394/status')
        doublequote_dict = json.dumps(rika_dict.json())
        print(doublequote_dict)
        print()

        usuable_dict = json.loads(doublequote_dict)
        controls_dict = (usuable_dict["controls"])
        sensors_dict = (usuable_dict["sensors"])
        stoveFeatures = (usuable_dict["stoveFeatures"])
        #print(sensors_dict)

        inputRoomTemperature_value = (sensors_dict["inputRoomTemperature"])
        measurement = "inputRoomTemperature"
        RikaData(location, measurement, float(inputRoomTemperature_value))
        _send_rika_data_to_influxdb(RikaData)

        inputFlameTemperature_value = (sensors_dict["inputFlameTemperature"])
        parameterRuntimePellets_value = (sensors_dict["parameterRuntimePellets"])
        parameterFeedRateTotal_value = (sensors_dict["parameterFeedRateTotal"])
        parameterFeedRateService_value = (sensors_dict["parameterFeedRateService"])

        print('Room     Temperature value : ' + str (inputRoomTemperature_value))
        print('Flame    Temperature value : ' + str (inputFlameTemperature_value))
        print('Runtime  Pellets value : ' + str (parameterRuntimePellets_value))
        print('FeedRate Total value : ' + str (parameterFeedRateTotal_value))
        print('FeedRate Service value : ' + str (parameterFeedRateService_value))



        onOff_value = (controls_dict["onOff"])
        operatingMode_value = (controls_dict["operatingMode"])
        heatingPower_value = (controls_dict["heatingPower"])
        targetTemperature_value = (controls_dict["targetTemperature"])
        ecoMode_value = (controls_dict["ecoMode"])

        print ('onOff value : ' + str (onOff_value))
        print ('operatingMode value : ' + str (operatingMode_value))
        print ('heatingPower value : ' + str (heatingPower_value))
        print ('targetTemperature value : ' + str (targetTemperature_value))
        print ('ecoMode value : ' + str (ecoMode_value))

        #if rika_data is not None:
        #    send_rika_data_to_influxdb(rika_data)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

