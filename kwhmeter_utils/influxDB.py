from datetime import date, timedelta, datetime
from influxdb import InfluxDBClient
import time
from .common import config_export2



def to_influxDB(datos,consumos):
    influxDB=config_export2['influxDB']
    client = InfluxDBClient(host=influxDB['host'], port=influxDB['port'], username=influxDB['user'], password=influxDB['password'] )
    client.create_database(influxDB['db'])
    client.switch_database(influxDB['db'])
    print(client.get_list_database())
    name=datos['name']
    cups=datos['cups']
    json_body=[]
    for v in consumos.itertuples():
        json_body = json_body + [
        {
            "measurement": "ELECTRICIDAD",
            "tags": {
                "CUPS": cups,
                "domicilio": name
            },
            "time": v.Index,
            "fields": {
                "kWh": v.consumo
            }
        },
        ]
    print(json_body)
    client.write_points(json_body)        

