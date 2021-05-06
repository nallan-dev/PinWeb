import locale
import sys
from pathlib import Path


# ==========================================================================
DEBUG = False
ALLOWED_HOSTS = ['*']  # Only for private network!
INVERSE_STATE = True  # invert GPIO (if your device activates by GPIO.LOW)
WEB_APP_PORT = 8080  # Port of this Django-app
FAKE_GPIO = True  # For use on raspberry set to False here
USE_SCHEDULE = True  # Don't show in interfaces and don't launch in background
USE_SENSOR = True  # Same as schedule - use sensor DHT(11,21,22) (GPIO-4)
USE_BOT = True  # launch telegram bot process in background

# Telegram bot conf in web admin panel (if change token - app restart required)

# Internationalization
LANGUAGE = 'en'  # supports only 'ru' and 'en'
TIME_ZONE = 'Europe/Moscow'

# All 26 GPIO BOARD nums available for use (except GPIO4 (BOARD7) for sensor)
BOARD_NUMS = [3, 5, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29,
              31, 32, 33, 35, 36, 37, 38, 40]
# works for Pi1 Model B+, Pi 2B, Pi Zero, Pi 3B, and Pi 4B
# remove some if you want exclude them from list of available
# (make sure that existing pins in db doesn't already use this num, in that
#  case delete them first in admin panel, than remove here and restart app
SENSOR_NUM = 4  # GPIO.BCM (Board-7)
# ==========================================================================


#
# Path to folder with manage.py
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'slx67e$%j)g*7qfw^jf^z(n%dut@w6#nfm=f=3e=bt(&4fcyj2'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'relay_app.apps.RelayAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/


USE_I18N = True

USE_L10N = True

USE_TZ = True
if LANGUAGE == 'ru':
    LANGUAGE_CODE = 'ru-ru'
    LOCALE = ('RU', 'UTF8')
elif LANGUAGE == 'en':
    LANGUAGE_CODE = 'en-us'
    LOCALE = ('EN', 'UTF8')

SENSOR_OUT_PATH = BASE_DIR / 'main' / 'sensor_data.json'
#
try:
    locale.setlocale(locale.LC_ALL, LOCALE)
except NameError as e:
    s = 'Unknown language - check LANGUAGE=  in settings.py, ' \
        'supports only "ru" and "en"'
    raise NameError(s)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
