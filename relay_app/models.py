from django.db import models
from django.conf import settings
from .validators import validate_cron, CRON_URL
from .switch_gpio import switch_gpio
from main.translations import t


class PinDataQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            ret_code = switch_gpio(obj.board_num, False)
            if ret_code:  # assume error here
                return  # dont delete
        super(PinDataQuerySet, self).delete()


class PinData(models.Model):
    BOARD_CHOICES = [(i, 'BOARD-' + str(i)) for i in settings.BOARD_NUMS]

    objects = PinDataQuerySet.as_manager()

    order_id = models.PositiveIntegerField(verbose_name=t('Порядковый номер'),
                                        help_text=t('Для отображения в списке'),
                                        unique=True)
    board_num = models.IntegerField(verbose_name=t('Номер пина (BOARD)'),
                                   help_text=t('Нумерация GPIO BOARD'),
                                   unique=True,
                                   choices=BOARD_CHOICES)
    command = models.CharField(max_length=30, unique=True,
                               verbose_name=t('Назначение переключателя'),
                               help_text=t('Например "Свет на кухне"'))
    comment = models.CharField(max_length=250, verbose_name=t('Комментарий'),
                               help_text=t('Необязательное поле'),
                               blank=True, null=True)
    state = models.BooleanField(default=False,
                                verbose_name=t('Текущее состояние'),
                                help_text=t('Включен или выключен'))
    visible = models.BooleanField(default=True, verbose_name=t('Активен'),
                                  help_text=t('Отображать ли в интерфейсах? ('
                                              'GPIO пин инициализируется в '
                                              'любом случае)'))

    class Meta:
        ordering = ['order_id']
        verbose_name = t('Настройка пина')
        verbose_name_plural = '  ' + t('Настройки пинов')

    def __str__(self):
        return self.command

    @property
    def action_name(self):
        return '"' + self.command + '"'

    def as_dict(self):
        return {'order_id': self.order_id,
                'board_num': self.board_num,
                'command': self.command,
                'comment': self.comment,
                'state': self.state,
                'command_verbose': self.action_name}

    def save(self, *args, **kwargs):
        ret_code = switch_gpio(self.board_num, self.state)
        if ret_code:  # assume error here
            return
        super(PinData, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret_code = switch_gpio(self.board_num, False)
        if ret_code:  # assume error here
            return
        super(PinData, self).delete(*args, **kwargs)


class BotConfig(models.Model):
    ID_CHOICES = [('TELEGRAM_TOKEN', t('Токен телеграм-бота')),
                  ('ALLOWED_CLIENTS', t('Разрешенные id (через запятую)'))]
    id = models.CharField(max_length=40, choices=ID_CHOICES,
                          verbose_name=t('Идентификатор'),
                          help_text=t('Идентификатор параметра'),
                          primary_key=True)
    value = models.CharField(max_length=400,
                             verbose_name=t('Значение'),
                             help_text=t('Значение параметра'))

    class Meta:
        ordering = ['id']
        verbose_name = t('Настройка телеграм-бота')
        verbose_name_plural = t('Настройки телеграм-бота')

    def __str__(self):
        return self.id

    @staticmethod
    def get_allowed_ids():
        try:
            bot_config = BotConfig.objects.get(id='ALLOWED_CLIENTS')
        except models.ObjectDoesNotExist:
            return []
        value = bot_config.value
        if ',' in value:
            allowed_clients = [s.strip() for s in value.split(',')]
        else:
            allowed_clients = [value.strip()]
        return allowed_clients


class ScheduleConfig(models.Model):
    ACT_CHOICES = [(1, t('Включать')),
                   (0, t('Выключать')),
                   (2, t('Переключать'))]
    pin_data = models.ForeignKey(PinData, on_delete=models.CASCADE,
                                 related_name='schedules',
                                 verbose_name=t('Переключатель'))
    cron_time = models.CharField(max_length=100, default='* * * * *',
                                 verbose_name=t('Время срабатывания'),
                                 help_text=t('Нотация Cron, удобно составлять')
                                           + ' ' + CRON_URL,
                                 validators=[validate_cron])
    describe_cron = models.CharField(max_length=200, default=t('Каждую минуту'),
                                 verbose_name=t('Описание времени выполнения'))
    action = models.PositiveSmallIntegerField(choices=ACT_CHOICES,
                                              verbose_name=t('Действие'),
                                    help_text=t('Действие над переключателем'))
    active = models.BooleanField(default=True, verbose_name=t('Активно'),
                                 help_text=t('Активна ли эта задача'))
    comment = models.CharField(max_length=200, verbose_name=t('Комментарий'),
                               blank=True, null=True)

    class Meta:
        ordering = ['pin_data']
        verbose_name = t('Настройка задачи по таймеру')
        verbose_name_plural = '  ' + t('Настройки задач по таймеру')

    def __str__(self):
        return str(self.pin_data) + ' ' + str(self.action)

    @property
    def pin_name(self):
        return self.pin_data.action_name

    pin_name.fget.short_description = t('Переключатель')

    def as_dict(self):
        return {'id': self.pk,
                'pin_board_num': self.pin_data.board_num,
                'pin_command': self.pin_name,
                'cron_time': self.cron_time,
                'cron_verbose': self.describe_cron.lower(),
                'action': self.action,
                'action_name': self.get_action_name(),
                'active': int(self.active),
                'full_report': self.get_full_report()}

    def get_action_name(self):
        for value, verbose in ScheduleConfig.ACT_CHOICES:
            if self.action == value:
                return verbose

    def get_full_report(self):
        return '{0} {1} {2}'.format(self.get_action_name().capitalize(),
                                    self.pin_name.lower(),
                                    self.describe_cron.lower())


class TemperConfig(models.Model):
    ACT_CHOICES = [(1, t('Включать')), (0, t('Выключать'))]
    TEMP_CHOICES = [('t_greater', t('при температуре более чем')),
                    ('t_less', t('при температуре менее чем')),
                    ('h_greater', t('при влажности более чем')),
                    ('h_less', t('при влажности менее чем'))]
    pin_data = models.ForeignKey(PinData, on_delete=models.CASCADE,
                                 related_name='tempers',
                                 verbose_name=t('Переключатель'))
    compare_data = models.CharField(max_length=10, verbose_name=t('Сравнение'),
                                    help_text=t('Сравнение показателя'),
                                    choices=TEMP_CHOICES)
    num_data = models.SmallIntegerField(verbose_name=t('Значение'),
                                        help_text=t('Значение параметра (граду'
                                                    'сы цельсия или проценты '
                                                    'влажности)'))
    reverse = models.BooleanField(default=False,
                                  verbose_name=t('Иначе выполнять обратное'),
                                 help_text=t('Для "Включать при температуре ме'
                                             'нее чем 18 градусов", при повы'
                                             'шении выше 18 градусов сразу '
                                             'выполнит обратное действие - '
                                             'выключит.'))
    action = models.PositiveSmallIntegerField(choices=ACT_CHOICES,
                                              verbose_name=t('Действие'),
                                    help_text=t('Действие над переключателем'))
    active = models.BooleanField(default=True, verbose_name=t('Активно'),
                                 help_text=t('Активна ли эта задача'))
    cron_time = models.CharField(max_length=100, default=None,
                                 null=True, blank=True,
                                 verbose_name=t('Время срабатывания'),
                                 help_text=t('Нотация Cron, удобно составлять')
                                             + ' ' + CRON_URL,
                                 validators=[validate_cron])
    describe_cron = models.CharField(max_length=200, default=None,
                                     null=True, blank=True,
                                verbose_name=t('Описание времени выполнения'))

    class Meta:
        ordering = ['pin_data']
        verbose_name = t('Настройка задачи по датчику')
        verbose_name_plural = ' ' + t('Настройки задач по датчику')

    def __str__(self):
        return str(self.pin_data) + ' ' + str(self.action)

    @property
    def num_data_with_unit(self):
        return str(self.num_data) + self.get_unit()

    num_data_with_unit.fget.short_description = t('Значение')

    @property
    def pin_name(self):
        return self.pin_data.action_name

    pin_name.fget.short_description = t('Переключатель')

    def get_temp_choise_verbose(self):
        for c in TemperConfig.TEMP_CHOICES:
            if self.compare_data == c[0]:
                return c[1]

    def get_action_name(self):
        for value, verbose in TemperConfig.ACT_CHOICES:
            if self.action == value:
                return verbose

    def get_unit(self):
        if 't_' in self.compare_data:
            return '℃'
        else:
            return '%'

    def get_reverse_verbose(self, prefix=', '):
        if self.reverse:
            if self.action:
                return prefix + t('иначе выключать')
            else:
                return prefix + t('иначе включать')
        else:
            return ''

    def get_timer_description(self, prefix=', '):
        s = ''
        if self.cron_time and self.describe_cron:
            s = prefix + self.describe_cron.lower()
        return s

    def as_dict(self):
        return {'id': self.pk,
                'pin_board_num': self.pin_data.board_num,
                'pin_command': self.pin_name,
                'compare_data': self.compare_data,
                'compare_data_verbose': self.get_temp_choise_verbose(),
                'num_data': self.num_data,
                'reverse': self.reverse,
                'unit': self.get_unit(),
                'action': self.action,
                'action_name': self.get_action_name(),
                'active': int(self.active),
                'cron_time': self.cron_time,
                'cron_verbose': self.describe_cron,
                'full_report': self.get_full_report()}

    def get_full_report(self):
        return '{0} {1} {2} {3}'.format(self.get_action_name().capitalize(),
                                        self.pin_name.lower(),
                                        self.get_temp_choise_verbose(),
                                        self.num_data_with_unit) + \
                self.get_reverse_verbose() + self.get_timer_description()


def init_pin_state():
    try:
        for elem in PinData.objects.all().only('board_num', 'state'):
            switch_gpio(elem.board_num, elem.state)
    except Exception as e:
        print('In init_pin_state warning:', e)


init_pin_state()  # run once when app process starts
