#!/usr/bin/env python3
# encoding=utf-8

import lnetatmo
from influxdb import InfluxDBClient

# Netatmo configuration - edit these
CLIENT_ID = ''
CLIENT_SECRET = ''
USERNAME = ''
PASSWORD = ''

# influx configuration - edit these
ifuser = ''
ifpass = ''
ifdb   = ''
ifhost = '127.0.0.1'
ifport = 8086


authorization = lnetatmo.ClientAuth(
        clientId=CLIENT_ID,
        clientSecret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        scope='read_station'
        )
weatherData = lnetatmo.WeatherStationData(authorization)


client = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
if {'name': ifdb} not in client.get_list_database():
    client.create_database(ifdb)

for station in weatherData.stations:
    station_data = []
    module_data = []
    station = weatherData.stationById(station)
    station_name = station['station_name']
    altitude = station['place']['altitude']
    country= station['place']['country']
    timezone = station['place']['timezone']
    longitude = station['place']['location'][0]
    latitude = station['place']['location'][1]
    weatherData.default_station_data = weatherData.stationByName(station_name)
    for module, moduleData in weatherData.lastData(exclude=3600).items():
        for measurement in ['altitude', 'country', 'longitude', 'latitude', 'timezone']:
            value = eval(measurement)
            if type(value) == int:
                value = float(value)
            station_data.append({
                "measurement": measurement,
                "tags": {
                    "station": station_name,
                    "module": module
                },
                "time": moduleData['When'],
                "fields": {
                    "value": value
                }
            })

        for sensor, value in moduleData.items():
            if sensor.lower() != 'when':
                if type(value) == int:
                    value = float(value)
                module_data.append({
                    "measurement": sensor.lower(),
                    "tags": {
                        "station": station_name,
                        "module": module
                    },
                    "time": moduleData['When'],
                    "fields": {
                        "value": value
                    }
                })

    client.write_points(station_data, time_precision='s', database=ifdb)
    client.write_points(module_data, time_precision='s', database=ifdb)
