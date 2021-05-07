import logging
import atexit
from django.conf import settings


active_pins = {}  # Global object to hold real pin states
logger = logging.getLogger('GPIO_handler')


class GpioDummy:
    BOARD = 'BOARD'
    OUT = 'OUT'

    @classmethod
    def setmode(cls, *args):
        print('GPIO setmode', args)

    @classmethod
    def output(cls, *args):
        print('SET GPIO OUT', args)

    @classmethod
    def setup(cls, *args, **kwargs):
        print('GPIO setup', args, kwargs)

    @classmethod
    def cleanup(cls):
        print('GPIO cleanup')

    @classmethod
    def input(cls, *args):
        print('GPIO check state')


if settings.FAKE_GPIO:
    GPIO = GpioDummy
else:
    try:
        import RPi.GPIO as GPIO
    except Exception as e:
        s = '{0} - Are you on raspberry? If yes, try install it via pip. ' \
            'If not, set FAKE_GPIO = True in settings.py'.format(e)
        raise EnvironmentError(s)
GPIO.setmode(GPIO.BOARD)


def switch_gpio(board_num, state, invert_state):
    if board_num not in settings.BOARD_NUMS:
        return 1
    try:
        state = bool(int(state))
        state = not state if invert_state else state
        if board_num not in active_pins:
            GPIO.setup(board_num, GPIO.OUT, initial=state)
            active_pins[board_num] = state
        else:
            if active_pins[board_num] != state:
                GPIO.output(board_num, state)
                active_pins[board_num] = state
    except Exception as e:
        logger.critical('Err while switching GPIO num {0} {1} {2}'
                        ''.format(board_num, type(e), e))
        return 1


@atexit.register
def clean_up():
    GPIO.cleanup()
    print('Cleaned up at exit')
