from main.translations import t


def get_context_extras():
    return {'title': t('Переключатели'),
            'no_switches': t('Здесь пока нет переключателей - настройте их'),
            'sensor_expired': t('Устаревшие данные датчика'),
            'updated': t('Обновлено'),
            'schedule_tasks_title': t('Плановые задачи'),
            'temper_tasks_title': t('Задачи по температуре и влажности')}
