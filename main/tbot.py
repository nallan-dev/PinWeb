import sqlite3
import telebot
import requests
import json
import sys
import traceback
import copy
import time
import subprocess
from settings import WEB_APP_PORT, DATABASES, USE_SENSOR, USE_SCHEDULE
from translations import t


# ============================ conf ========================================
DB_PATH = DATABASES['default']['NAME']
# ==========================================================================
WEB_APP_ADDR = 'http://localhost:{0}/'.format(WEB_APP_PORT)


ON_S = "\U0001F31D"  # emoji on switcher
OFF_S = "\U0001F31A"
TEMP = "\U0001F321"
HUM = "\U0001F4A7"


def get_token():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT `value` FROM `relay_app_botconfig` WHERE `id` = '
                   '"TELEGRAM_TOKEN";')
    return cursor.fetchone()[0]


try:
    token = get_token()
    bot = telebot.TeleBot(token, threaded=False)
except Exception as e:
    print('\nCheck db, token and connections! ', type(e), e)
    sys.exit(1)


def get_relay_data(resp=None):
    if resp is None:
        resp = requests.get(WEB_APP_ADDR + 'get_report/', timeout=3)
    relay_data = json.loads(resp.text)
    relay_data = form_keyboard_and_command_list(relay_data)
    relay_data = form_keyboard_and_timers_report(relay_data)
    relay_data = form_sensor_msg(relay_data)
    return relay_data


def form_keyboard_and_command_list(relay_data):
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=False)
    valid_commands = {}
    rows_list = []
    for relay in relay_data['pin_data']:
        cmd, cmd_opp = (ON_S, OFF_S) if relay['state'] else (OFF_S, ON_S)
        cmd_str = cmd + ' ' + relay['name'].lower()
        cmd_str_opposite = cmd_opp + ' ' + relay['name'].lower()
        rows_list.append(cmd_str)
        relay_opp = copy.deepcopy(relay)
        relay_opp['state'] = not relay_opp['state']
        valid_commands[cmd_str] = relay_opp
        valid_commands[cmd_str_opposite] = relay
    for row in chunks(rows_list, 2):
        keyboard.row(*row)
    keyboard.row(t('Обновить статус'))
    if (relay_data['use_sensor'] or relay_data['use_schedule']) and \
                                    (relay_data.get('schedule_data', []) or
                                     relay_data.get('temper_data', [])):
        keyboard.row(t('Автоматические переключения'))
    relay_data['relay_keyboard'] = keyboard
    relay_data['relay_valid_commands'] = valid_commands
    return relay_data


def form_keyboard_and_timers_report(relay_data):
    if not relay_data['use_schedule'] and not relay_data['use_schedule']:
        return relay_data

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    command_dict = {}
    schedules = relay_data.get('schedule_data', [])
    temper_data = relay_data.get('temper_data', [])
    msg = t('Плановые задачи') + ':\n\n'
    i = 0
    for i, s in enumerate(schedules):
        emoji = ON_S if s['active'] else OFF_S
        row = '{i}) {emoji} {report}\n\n' \
              ''.format(i=i+1, emoji=emoji, report=s['full_report'])
        msg += row
        action = 0 if s['active'] else 1
        new_action_name = t('Активировать') if action else t('Деактивировать')
        button = '{0} {1} №{2}'.format(new_action_name, t('таймер'), i+1)
        command_dict[button] = {'sched_id': s['id'], 'state': action}
        keyboard.row(button)
    if not schedules:
        if relay_data['use_schedule']:
            msg = t('Нет переключений по таймеру\n\n')
        else:
            msg = ''
        i = -1
    if temper_data:
        i += 1
        msg += t('Задачи по температуре и влажности') + ':\n\n'
        for j, temp in enumerate(temper_data):
            emoji = ON_S if temp['active'] else OFF_S
            row = '{i}) {emoji} {report}\n\n' \
                  ''.format(i=i+j+1, emoji=emoji, report=temp['full_report'])
            msg += row
            action = 0 if temp['active'] else 1
            new_action_name = t('Активировать') if action \
                                                    else t('Деактивировать')
            button = '{0} {1} №{2}'.format(new_action_name, t('правило'),
                                           i + j + 1)
            command_dict[button] = {'temper_id': temp['id'], 'state': action}
            keyboard.row(button)
    keyboard.row(t('Назад'))
    relay_data['sched_msg'] = msg
    relay_data['sched_keyboard'] = keyboard
    relay_data['sched_valid_commands'] = command_dict
    return relay_data


def form_sensor_msg(relay_data):
    temper_msg = ''
    if relay_data['use_sensor']:
        c = relay_data['current_temper']
        fresh_date = c['verbose_time']
        expired_msg = ''
        if c['expired']:
            fresh_date = c['verbose_datetime']
            expired_msg = '\n' + t('Устаревшие данные датчика') + '!'
        temper_msg = '{0} {1}℃   {2} {3}%\n({4} {5}){6}' \
                     ''.format(TEMP, c['temp'], HUM, c['humidity'],
                               t('Обновлено'), fresh_date, expired_msg)
    relay_data['temper_msg'] = temper_msg
    return relay_data


def switch_pin(relay):
    r = requests.post(WEB_APP_ADDR, data={'board_num': relay['board_num'],
                                          'state': int(relay['state'])},
                      verify=False, timeout=3)
    return r


def switch_timer(data):
    r = requests.post(WEB_APP_ADDR, data=data, verify=False, timeout=3)
    return r


def ifconfig():
    try:
        out = subprocess.check_output('ifconfig', shell=True)
    except Exception as e:
        out = '{0} {1}'.format(type(e), e)
    return out


# main router
@bot.message_handler(content_types=['text'])
def run(message):
    def handle_relay_switch():
        nonlocal r
        resp = switch_pin(r['relay_valid_commands'][message.text])
        msg = 'OK'
        r = get_relay_data(resp)
        bot.send_message(message.chat.id, msg, reply_markup=r['relay_keyboard'])

    def handle_timer_list():
        bot.send_message(message.chat.id, r['sched_msg'],
                         reply_markup=r['sched_keyboard'])

    def handle_timer_switch():
        nonlocal r
        resp = switch_timer(r['sched_valid_commands'][message.text])
        r = get_relay_data(resp)
        bot.send_message(message.chat.id, r['sched_msg'],
                         reply_markup=r['sched_keyboard'])

    # =================================================================
    if (int(time.time()) - message.date) > 30:  # old messages
        return  # ignore
    if message.text == '*ifconfig*':
        bot.send_message(message.chat.id, ifconfig())
    try:
        r = get_relay_data()
        allowed_id = r.get('allowed_clients', [])
        err = ''
    except requests.exceptions.ConnectionError as e:
        print(type(e), e, traceback.format_exc())
        err, allowed_id = ' (web_app is unavailable)', []
        r = {}
    else:
        if not r['use_bot']:
            err, allowed_id = ' (turn on USE_BOT in settings)', []
    if str(message.chat.id) not in allowed_id:
        bot.send_message(message.chat.id,
                         'ACCESS DENIED - ' + str(message.chat.id) + err)
        return
    # =================================================================
    if message.text in r.get('relay_valid_commands', {}).keys():
        handle_relay_switch()
    elif message.text in (t('Обновить статус'), t('Назад')):
        text = 'OK' + '  ' + r.get('temper_msg', '')
        bot.send_message(message.chat.id, text,
                         reply_markup=r['relay_keyboard'])
    elif message.text == t('Автоматические переключения'):
        handle_timer_list()
    elif message.text in r.get('sched_valid_commands', {}).keys():
        handle_timer_switch()
    elif message.text == '/start':
        bot.send_message(message.chat.id, t('Погнали!'),
                         reply_markup=r['relay_keyboard'])
    else:
        bot.send_message(message.chat.id, t('Команда не распознана'),
                         reply_markup=r['relay_keyboard'])


if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print(type(e), e, traceback.format_exc())
            time.sleep(3.0)
