# coding: utf-8
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from gamblings.models import Gambling, GamblingConfiguration, GamblingResult, GamblingSummary
import urllib, re, json, subprocess, os
from datetime import datetime

def gambling_result(request):

  gambling_name = request.GET['gambling_name']
  a_date = datetime.strptime(request.GET['date'], '%Y-%m-%d').date() 

  g = get_object_or_404(Gambling, name=gambling_name)
  
  gr = get_object_or_404(GamblingResult, gambling=g, date=a_date)

  result = []
  numbers = gr.result_as_list()
  for i in xrange(10):
    result.append([i+1, numbers[i], i+11, numbers[i+10]])

  print result

  model = {'display_name': g.display_name, 'result': result}
  
  return render_to_response('gambling_result.html', model )

def gambling_summaries(request):

  a_date = datetime.strptime(request.GET['date'], '%Y-%m-%d').date() 
  today = a_date.weekday()
  summary_name = request.GET['summary_name']

  gambling_summaries = GamblingSummary.objects.filter(name=summary_name, days_of_week__contains=today).prefetch_related('gamblings')

  if gambling_summaries and len(gambling_summaries) == 1:
    summary = gambling_summaries[0]
    gamblings = summary.gamblings

    gambling_results_to_display = []
    for g in gamblings.all():
      result = GamblingResult.objects.filter(gambling=g, date=a_date)
      table_of_numbers = []
      if result:
        r = result[0].result_as_list()
        for i in xrange(5):
          table_of_numbers.append([
            (i+1, r[i]),
            (i+6, r[i+5]),
            (i+11, r[i+10]),
            (i+16, r[i+15]) 
          ])
      else:
        for i in xrange(5):
          table_of_numbers.append([
            (i+1, ''),
            (i+6, ''),
            (i+11, ''),
            (i+16, '') 
          ])

      gambling_results_to_display.append({
        'display_name': g.display_name,
        'date': a_date,
        'table_of_numbers': table_of_numbers
      })

    return render_to_response('gambling_summary.html', {'gambling_results': gambling_results_to_display})

  else:
    raise Http404
