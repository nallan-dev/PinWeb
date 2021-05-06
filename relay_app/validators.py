import pycron
import cron_descriptor
from django.core.exceptions import ValidationError
from main.translations import t


CRON_URL = '<a href="https://crontab.guru/" target="blank">' + \
                t('здесь') + '</a>'


def validate_cron(cron_str):
    valid_chars = '-/,*0123456789 '
    e = t('Невалидная нотация. Строка должна содержать только знаки {0}'
        ', и четыре одинарных пробела. Удобно настроить и скопировать строку'
        ' можно здесь{1}')
    e = e.format(valid_chars, ' - https://crontab.guru/')
    try:
        pycron.is_now(cron_str)
        cron_descriptor.get_description(cron_str)
    except Exception:
        raise ValidationError(e)
    spaces_counter = 0
    for char in cron_str:
        if char == ' ':
            spaces_counter += 1
        if char not in valid_chars:
            raise ValidationError(e)
    if spaces_counter != 4:
        raise ValidationError(e)
    return cron_str


def validate_pin_params(pin_num=None, schedule_id=None, temper_id=None,
                        state=None):
    if pin_num and pin_num.isdigit():
        if state and state.isdigit():
            return True
    elif schedule_id and schedule_id.isdigit():
        if state and state.isdigit():
            return True
    elif temper_id and temper_id.isdigit():
        if state and state.isdigit():
            return True
    else:
        return False
