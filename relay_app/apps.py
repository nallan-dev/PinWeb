from django.apps import AppConfig
from main.translations import t


class RelayAppConfig(AppConfig):
    name = 'relay_app'
    verbose_name = ' ' + t('Переключатели')
