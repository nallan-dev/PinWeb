import json
import time
import pytz
from datetime import datetime
from django.conf import settings


local_tz = pytz.timezone(settings.TIME_ZONE)


def parse_sensor():
    try:
        with open(settings.SENSOR_OUT_PATH, 'r') as f:
            data = json.loads(f.read())
            data['expired'] = False
            data['verbose_time'], data['verbose_datetime'] = \
                                                verbose_time(data['last_time'])
        if time.time() - data['last_time'] > 30:
            data['expired'] = True
    except Exception as e:
        data = {}
    return data


def verbose_time(timestamp):
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    l_dt = local_tz.normalize(utc_dt.astimezone(local_tz))
    return l_dt.strftime("%H:%M:%S"), l_dt.strftime("%d.%m.%Y %H:%M:%S")
