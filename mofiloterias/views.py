# coding: utf-8
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from gamblings.models import Gambling, GamblingSummary, GamblingConfiguration, GamblingResult
from mofiloterias.models import Event
from mofiloterias import today, now
from datetime import timedelta, date

import json


def index(request):
  glamblings = Gambling.objects.values('name', 'display_name')

  last_gambling_date = get_date_for_last_gambling()

  summaries = GamblingSummary.objects.filter(days_of_week__contains=last_gambling_date.weekday())
  gs = []
  for s in summaries:
    print s.gamblings.all()
    heads = []
    for g in s.gamblings.all():
      r = GamblingResult.objects.filter(gambling=g, date=last_gambling_date)
      ret = {}
      ret['name'] = g.name
      ret['display_name'] = g.display_name
      ret['date'] = last_gambling_date
      ret['head_result'] = r.result[0] if r else None
      heads.append(ret)
    gs.append(heads)

  summaries_names = map(lambda s: s.name, summaries)
  print summaries_names

  return render_to_response('index.html', 
    {'gamblings': glamblings, 'summaries': summaries_names, 'date': last_gambling_date, 'gamblings_summaries': gs} )


def events(request):
  events = Event.objects.all().order_by('-id')[:10]

  last_events_as_str = map(lambda x: str(x), events)

  return HttpResponse(json.dumps(last_events_as_str), mimetype="application/json")


def get_date_for_last_gambling():
  date = today()
  time = now()
  any_gambling_today = GamblingConfiguration.objects.filter(days_of_week__contains=date.weekday(), time__lt=time)

  if any_gambling_today:
    return date
  else:
    if date.weekday == 0:
      return date - timedelta(2)
    else:
      return date - timedelta(1)

