import datetime
import itertools
import json
import logging

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import utc

from django.views.decorators.csrf import csrf_exempt

from owntracks.models import OwnTrackLog

logger = logging.getLogger(__name__)


# Create your views here.
@csrf_exempt
def manage_owntrack_log(request):
    try:
        s = json.loads(request.read().decode('utf-8'))
        tid = s['tid']
        lat = s['lat']
        lon = s['lon']
        logger.info('tid: {tid}.lat: {lat}.lon: {lon}'.format(tid=tid, lat=lat, lon=lon))
        if tid and lat and lon:
            o = OwnTrackLog()
            o.tid = tid
            o.lat = lat
            o.lon = lon
            o.save()
            return HttpResponse('ok')
        else:
            return HttpResponse('data error')

    except Exception as e:
        logger.error(e)
        return HttpResponse('error')


@login_required
def show_maps(request):
    if request.user.is_superuser:
        defaultdate = str(datetime.datetime.now().date())
        date = request.GET.get('date', defaultdate)
        context = {
            'date': date,
        }
        return render(request, 'ownstracks/show_maps.html', context)
    else:
        return HttpResponseForbidden()


@login_required
def show_log_dates(request):
    dates = OwnTrackLog.objects.values_list('created_time', flat=True)
    results = list(sorted(set(map(lambda x: x.strftime('%Y-%m-%d'), dates))))
    context = {
        'results': results,
    }
    return render(request, 'owntracks/show_log_dates.html', context)


def convert_to_amap(locations):
    convert_result = []
    it = iter(locations)

    item = list(itertools.islice(it, 30))
    while item:
        datas = ';'.join(set(map(lambda x: str(x.lon) + ',' + str(x.lat), item)))
        key = ''
        api = 'http://restapi.amap.com/v3/assistant/coordinate/convert'
        query = {
            'key': key,
            'locations': datas,
            'coordsys': 'gps',
        }
        resp = requests.get(url=api, params=query)
        result = json.loads(resp.text)
        convert_result.append(result['locations'])
        item = list(itertools.islice(it, 30))

    return ';'.join(convert_result)


@login_required
def get_datas(request):
    now = timezone.now().replace(tzinfo=utc)
    querydate = timezone.datetime(now.year, now.month, now.day, 0, 0, 0)
    if request.GET.get('date', None):
        date = list(map(lambda x: int(x), request.GET.get('date').split('-')))
        querydate = timezone.datetime(date[0], date[1], date[2], 0, 0, 0)

    querydate = timezone.make_aware(querydate)
    nextdate = querydate + datetime.timedelta(days=1)
    models = OwnTrackLog.objects.filter(created_time__range=(querydate, nextdate))
    result = list()
    if models and len(models):
        for tid, item in itertools.groupby(sorted(models, key=lambda k: k.tid), key=lambda k: k.tid):
            d = dict()
            d['name'] = tid
            paths = list()
            locations = convert_to_amap(sorted(item, key=lambda x: x.created_time))
            for i in locations.split(';'):
                paths.append(i.split(','))
            d['path'] = paths
            result.append(d)
    return JsonResponse(result, safe=False)
