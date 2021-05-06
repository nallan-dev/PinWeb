from django.contrib import admin
from django import forms
from django.conf import settings
from .models import PinData, BotConfig, ScheduleConfig, TemperConfig
from main.translations import t


admin.AdminSite.site_title = ' ' + t('Переключатели')

admin.AdminSite.site_header = t('Переключатели - администрирование')

admin.AdminSite.index_title = t('Приложения')

# Register your models here.


@admin.register(PinData)
class PinDataAdmin(admin.ModelAdmin):
    list_display = ('command', 'order_id', 'board_num', 'state', 'visible')
    # list_editable = ('command', 'board_num', 'state', 'visible')
    fields = (('order_id', 'board_num', 'visible'), 'command', 'comment')
    list_filter = ('visible', 'state')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(PinDataAdmin, self).formfield_for_dbfield(db_field,
                                                                    **kwargs)
        if db_field.name in ('comment',):
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield


if settings.USE_BOT:
    @admin.register(BotConfig)
    class BotConfigAdmin(admin.ModelAdmin):
        list_display = ('id', 'value')
        list_editable = ('value',)


if settings.USE_SCHEDULE:
    @admin.register(ScheduleConfig)
    class ScheduleConfigAdmin(admin.ModelAdmin):
        list_display = ('action', 'pin_name', 'describe_cron', 'active')
        list_filter = ('pin_data', 'active')
        fields = (('action', 'pin_data'), ('cron_time', 'describe_cron'),
                  'comment', 'active')

        class Media:
            js = ('js/cron_slug.js',)

        def formfield_for_dbfield(self, db_field, **kwargs):
            formfield = super(ScheduleConfigAdmin, self
                              ).formfield_for_dbfield(db_field,
                                                      **kwargs)
            if db_field.name in ('comment', 'describe_cron'):
                formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
            return formfield


if settings.USE_SENSOR:
    @admin.register(TemperConfig)
    class TemperConfigAdmin(admin.ModelAdmin):
        fieldsets = (
            (None, {
                'fields': ('action', 'pin_data', 'compare_data', 'num_data',
                           'reverse', 'active')
            }),
            (t('Настройки времени активности'), {
                'classes': ('collapse',),
                'fields': ('cron_time', 'describe_cron'),
                'description': t('Дополнительно можно ограничить время, в '
                                 'которое будет выполняться правило (например '
                                 'только ночью и т.п.).'),
            }),
        )

        list_display = ('action', 'pin_name', 'compare_data',
                        'num_data_with_unit', 'reverse', 'view_describe_cron',
                        'active')
        list_filter = ('pin_data', 'active')

        def view_describe_cron(self, instance):
            return instance.describe_cron

        view_describe_cron.empty_value_display = t('Всегда')
        view_describe_cron.short_description = t('Время срабатывания')
        # fields = ('action', 'pin_data', 'compare_data', 'num_data',
        #           'reverse', 'active')

        class Media:
            js = ('js/cron_slug.js',)

        def formfield_for_dbfield(self, db_field, **kwargs):
            formfield = super(TemperConfigAdmin, self
                              ).formfield_for_dbfield(db_field, **kwargs)
            if db_field.name in ('describe_cron',):
                formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
            return formfield
