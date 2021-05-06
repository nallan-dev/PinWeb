import requests
import json
import traceback
import time
import pycron
import datetime
from settings import WEB_APP_PORT, USE_SENSOR, USE_SCHEDULE


WEB_APP_ADDR = 'http://localhost:{0}/'.format(WEB_APP_PORT)


def get_params():
    resp = requests.get(WEB_APP_ADDR + 'get_report/', timeout=5)
    data = json.loads(resp.text)
    return data


def switch_pin(pin_num, state):
    r = requests.post(WEB_APP_ADDR, timeout=3, data={'pin_num': pin_num,
                                                     'state': state})
    return r


def process_jobs(data):
    def get_relay(board_num):
        for relay in relays:
            if relay['board_num'] == board_num:
                return relay

    def process_schedule(sched):
        action = sched['action']
        pin_num = sched['pin_board_num']
        relay = get_relay(pin_num)
        if action == int(relay['state']):
            return
        elif action == 2:
            action = int(not relay['state'])
        switch_pin(pin_num, action)

    def check_temper_triggers(temper, current):
        check_t_1 = temper['compare_data'] == 't_less' and \
                                        current['temp'] < temper['num_data']
        check_t_2 = temper['compare_data'] == 't_greater' and \
                                        current['temp'] > temper['num_data']
        check_h_1 = temper['compare_data'] == 'h_less' and \
                                        current['humidity'] < temper['num_data']
        check_h_2 = temper['compare_data'] == 'h_greater' and \
                                        current['humidity'] < temper['num_data']
        check = check_t_1 or check_t_2 or check_h_1 or check_h_2
        return check

    def check_temper_schedule(temper):
        check = True
        if temper['cron_time'] and not pycron.is_now(temper['cron_time']):
            check = False
        return check

    def process_temper(temper):
        action = temper['action']
        pin_num = temper['pin_board_num']
        relay = get_relay(pin_num)
        if action != int(relay['state']):
            switch_pin(pin_num, action)

    relays = data['pin_data']

    if USE_SCHEDULE:
        schedules = [elem for elem in data['schedule_data'] if elem['active']]
        for sched in schedules:
            if pycron.is_now(sched['cron_time']):
                process_schedule(sched)
    if USE_SENSOR:
        tempers = [elem for elem in data['temper_data'] if elem['active']]
        current_temper = data['current_temper']
        use_sensor = data['use_sensor']
        if use_sensor and current_temper and not current_temper['expired']:
            for temper in tempers:
                if not check_temper_schedule(temper):
                    continue
                if check_temper_triggers(temper, current_temper):
                    process_temper(temper)
                else:
                    if temper['reverse']:
                        temper['action'] = int(not bool(temper['action']))
                        process_temper(temper)


def run():
    data = get_params()
    process_jobs(data)


if __name__ == '__main__':
    time.sleep(10)
    if USE_SCHEDULE or USE_SENSOR:
        while True:
            second = datetime.datetime.now().second
            if not second:  # at 0 second
                try:
                    run()
                except Exception as e:
                    print(type(e), e, traceback.format_exc())
                finally:
                    time.sleep(1.1)
            elif second % 5 == 0:  # every 5 seconds
                if USE_SENSOR:
                    try:
                        run()
                    except Exception as e:
                        print(type(e), e, traceback.format_exc())
                time.sleep(1.1)
            else:
                time.sleep(0.7)
