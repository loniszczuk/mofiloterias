# coding: utf-8
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from gamblings.models import Gambling, GamblingSummary
from mofiloterias.models import Event

import json


def index(request):
  glamblings = Gambling.objects.values('name', 'display_name')
  summaries = GamblingSummary.objects.distinct().values('name').order_by
  return render_to_response('index.html', {'gamblings': glamblings, 'summaries': summaries} )  


def events(request):
  events = Event.objects.all().order_by('-id')[:10]

  last_events_as_str = map(lambda x: str(x), events)

  return HttpResponse(json.dumps(last_events_as_str), mimetype="application/json")

  
