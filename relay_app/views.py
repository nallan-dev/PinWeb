import cron_descriptor
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.urls import path, reverse
from django.views.decorators.csrf import csrf_exempt
from .models import PinData, BotConfig, ScheduleConfig, TemperConfig
from .parse_sensor import parse_sensor
from .validators import validate_pin_params
from .context_extras import get_context_extras


@csrf_exempt
def switch(request):
    def get(template_name='index.html'):
        context = get_all_report(request, json=False)
        context.update(get_context_extras())
        return render(request, template_name, context=context)

    def post():
        pin_num = request.POST.get('board_num')
        schedule_id = request.POST.get('sched_id')
        temper_id = request.POST.get('temper_id')
        state = request.POST.get('state')
        from_button = request.POST.get('from_button')
        from_ajax = request.POST.get('html_for_ajax')
        url_add = ''
        if not validate_pin_params(pin_num, schedule_id, temper_id, state):
            return JsonResponse({'error': 'Unknown params'})
        if pin_num:
            pin = get_object_or_404(PinData, board_num=int(pin_num))
            pin.state = int(state)
            pin.save()
            url_add = '#relay'
        if schedule_id:
            shed = get_object_or_404(ScheduleConfig, pk=int(schedule_id))
            shed.active = int(state)
            shed.save()
            url_add = '#timer'
        if temper_id:
            temper = get_object_or_404(TemperConfig, pk=int(temper_id))
            temper.active = int(state)
            temper.save()
            url_add = '#temper'
        if from_button:  # e.g. disabled js in browser
            return redirect(reverse(switch) + url_add)
        elif from_ajax:
            return get(template_name='content.html')
        else:
            return get_all_report(request)

    if request.method == 'GET':
        return get()
    elif request.method == 'POST':
        return post()
    else:
        return JsonResponse({'error': 'Unknown request'})


def get_all_report(request, json=True):
    pin_data = [p.as_dict() for p in PinData.objects.filter(visible=True)]
    context = {'pin_data': pin_data,
               'use_sensor': False,
               'use_schedule': False,
               'use_bot': False}
    if settings.USE_SENSOR:
        t_data = [t.as_dict() for t in TemperConfig.objects.all()]
        context['temper_data'] = t_data
        context['current_temper'] = parse_sensor()
        context['use_sensor'] = True
    if settings.USE_SCHEDULE:
        s_data = [s.as_dict() for s in ScheduleConfig.objects.all()]
        context['schedule_data'] = s_data
        context['use_schedule'] = True
    if settings.USE_BOT:
        allowed_clients = BotConfig.get_allowed_ids()
        context['allowed_clients'] = allowed_clients
        context['use_bot'] = True
    if not json:
        return context
    return JsonResponse(context, safe=False, json_dumps_params={'indent': 4,
                                                       'ensure_ascii': False})


def ajax_html(request):
    context = get_all_report(request, json=False)
    context.update(get_context_extras())
    return render(request, 'content.html', context)


def describe_cron(request):
    cron_str = request.GET.get('cron_str', '')
    try:
        err = ''
        res = cron_descriptor.get_description(cron_str)
    except Exception as e:
        err = e
        res = 'Невалидный крон'
    return JsonResponse({"e": str(err), "cron_verb": res}, safe=False,
                        json_dumps_params={'indent': 4, 'ensure_ascii': False})


urlpatterns = [
    path('', switch, name='switch'),
    path('get_report/', get_all_report, name='get_report'),
    path('describe_cron/', describe_cron),
    path('ajax_html/', ajax_html, name='ajax_html')
]
