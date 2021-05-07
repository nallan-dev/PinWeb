from settings import LANGUAGE


RU_EN_DICT = {
    # page_context
    'Здесь пока нет переключателей - настройте их':
                                'There are no switches here yet - set them up',
    'Устаревшие данные датчика': 'Outdated sensor data',
    'Обновлено': 'Updated',
    'Плановые задачи': 'Planned tasks',
    'Задачи по температуре и влажности': 'Temperature and humidity tasks',

    # admin
    'Переключатели': 'Switchers',
    'Переключатели - администрирование': 'Switchers - administration',
    'Приложения': 'Apps',
    'Настройки времени активности': 'Additional - active at some time only',
    'Дополнительно можно ограничить время, в которое будет выполняться правило'
        ' (например только ночью и т.п.).': 'E.g. rule active only at night',
    'Всегда': 'Always',

    # tbot
    'Обновить статус': 'Refresh status',
    'Автоматические переключения': 'Triggers',
    'Активировать': 'Activate',
    'Деактивировать': 'Deactivate',
    'таймер': 'time trigger',
    'правило': 'sensor trigger',
    'Нет переключений по таймеру': 'No schedules configured yet',
    'Назад': 'Back',
    'Погнали!': 'Let\'s roll!',
    'Команда не распознана': 'Unknown command',

    # models
    'Порядковый номер': 'Index number',
    'Для отображения в списке': 'For ordering in list',
    'Номер пина (BOARD)': 'Pin num (BOARD)',
    'Нумерация GPIO BOARD': 'GPIO BOARD numbering',
    'Назначение переключателя': 'Switch name',
    'Например "Свет на кухне"': 'For example, "Light in the kitchen"',
    'Комментарий': 'Comment',
    'Необязательное поле': 'Optional field',
    'Текущее состояние': 'Current state',
    'Включен или выключен': 'On or off',
    'Активен': 'Active',
    'Отображать ли в интерфейсах?': 'Display in interfaces?',
    'Инвертировать состояние': 'Invert state',
    'Инвертировать состояние пинов на уровне GPIO (т.е. "Включенный пин" = '
        'GPIO.LOW (gnd))': 'Invert state at GPIO-level (e.g. "Enabled pin" = '
                           'GPIO.LOW (gnd))',
    'Настройка пина': 'Pin config',
    'Настройки пинов': 'Pin configs',

    'Токен телеграм-бота': 'Telegram bot token',
    'Разрешенные id (через запятую)': 'Allowed id (separated by commas)',
    'Идентификатор': 'Name',
    'Идентификатор параметра': 'Param name',
    'Значение': 'Value',
    'Значение параметра': 'Param value',
    'Настройка телеграм-бота': 'Telegram bot config',
    'Настройки телеграм-бота': 'Telegram bot configs',

    'Включать': 'Switch on',
    'Выключать': 'Switch off',
    'Переключать': 'Switch',
    'Переключатель': 'Pin',
    'Время срабатывания': 'Trigger time',
    'Нотация Cron, удобно составлять': 'Cron notation, easy to compose',
    'здесь': 'here',
    'Каждую минуту': 'Every minute',
    'Описание времени выполнения': 'Time trigger description',
    'Действие': 'Action',
    'Действие над переключателем': 'Pin action',
    'Активно': 'Active',
    'Активна ли эта задача': 'Is trigger active?',
    'Настройка задачи по таймеру': 'Schedule config',
    'Настройки задач по таймеру': 'Schedule configs',


    'при температуре более чем': 'at a temperature of more than',
    'при температуре менее чем': 'at a temperature less than',
    'при влажности более чем': 'with humidity more than',
    'при влажности менее чем': 'with humidity less than',
    'Сравнение': 'Comparison',
    'Сравнение показателя': 'Comparison of the indicator',
    'Значение параметра (градусы цельсия или проценты влажности)':
                'Parameter value (degrees Celsius or humidity percentage)',
    'Иначе выполнять обратное': 'Otherwise, do the opposite action',
    'Для "Включать при температуре менее чем 18 градусов", при повышении выше'
        ' 18 градусов сразу выполнит обратное действие - выключит.':
            'For "Switch on at a temperature less than 18 degrees", when it '
            'rises above 18 degrees, it will immediately perform the opposite '
            'action - Switch it off.',
    'Настройка задачи по датчику': 'Sensor task config',
    'Настройки задач по датчику': 'Sensor task configs',
    'иначе выключать': 'otherwise switch off',
    'иначе включать': 'otherwise switch on',

    'Невалидная нотация. Строка должна содержать только знаки {0}'
        ', и четыре одинарных пробела. Удобно настроить и скопировать строку'
        ' можно здесь{1}': 'Invalid notation. The string must contain only '
                           'characters {0}, and four single spaces. '
                           'Conveniently set up and copy the string'
                           ' you can here{1}',

}


def t(text):
    if LANGUAGE == 'en' and text in RU_EN_DICT:
        text = RU_EN_DICT[text]
    return text
