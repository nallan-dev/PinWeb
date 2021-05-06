import os, sys
import signal
import atexit
from subprocess import Popen, DEVNULL
from main.settings import WEB_APP_PORT, BASE_DIR, FAKE_GPIO
from main.settings import USE_SENSOR, USE_SCHEDULE, USE_BOT
from manage import main

sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'main'))

# python run_app.py  acts like
# python manage.py runserver 0.0.0.0:[port] --nothreading --noreload
# and launch in subprocess background job workers if enabled in settings

EXEC_PATH = sys.executable + ' '
SHEDULE_FILEPATH = str(BASE_DIR / 'main' / 'schedule_job_worker.py')
TEMPER_FILEPATH = str(BASE_DIR / 'main' / 'sensor_data_job_worker.py')
BOT_FILEPATH = str(BASE_DIR / 'main' / 'tbot.py')

ONLY_APP = True  # don't spawn subprocess (for debug reason)
if __name__ == '__main__':
    if len(sys.argv) == 1:
        if not ONLY_APP:
            if USE_SCHEDULE or USE_SENSOR:
                sched_cmd = EXEC_PATH + SHEDULE_FILEPATH
                shed_p = Popen(sched_cmd, shell=True,
                               stdout=DEVNULL, stderr=DEVNULL,
                               preexec_fn=os.setsid)

                @atexit.register
                def clean_shed():
                    os.killpg(os.getpgid(shed_p.pid), signal.SIGTERM)

            if USE_SENSOR and not FAKE_GPIO:
                gpiod_p = Popen('sudo pigpiod', shell=True,
                                stdout=DEVNULL, stderr=DEVNULL,
                                preexec_fn=os.setsid)
                temper_cmd = EXEC_PATH + TEMPER_FILEPATH
                temper_p = Popen(temper_cmd, shell=True,
                                 stdout=DEVNULL, stderr=DEVNULL,
                                 preexec_fn=os.setsid)


                @atexit.register
                def clean_temper():
                    os.killpg(os.getpgid(temper_p.pid), signal.SIGTERM)
                    os.killpg(os.getpgid(gpiod_p.pid), signal.SIGTERM)

            if USE_BOT:
                bot_cmd = '{0} {1}'.format(EXEC_PATH, BOT_FILEPATH)
                bot_p = Popen(bot_cmd, shell=True,
                              stdout=DEVNULL, stderr=DEVNULL,
                              preexec_fn=os.setsid)

                @atexit.register
                def clean_bot():
                    os.killpg(os.getpgid(bot_p.pid), signal.SIGTERM)

        sys.argv += ['runserver',
                     '0.0.0.0:' + str(WEB_APP_PORT),
                     '--nothreading',
                     '--noreload']
        main()
