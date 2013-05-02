from optparse import OptionParser
from mofiloterias import publish_event
from gamblings.models import GamblingConfiguration, GamblingResult, ImportEvent
from datetime import date, datetime, time

from gamblings.sources import *

sources = [
  NotitimbaSource(),
  LoteriasMundialesSource(),
  ViviTuSuerteSource()
]

def daterange(start_date, end_date):
  for n in range((end_date - start_date).days):
    yield start_date + timedelta(n)

def save_gambling_results_by_date(a_date):

  weekday = a_date.weekday()
  now = datetime.now()
  timenow = time(now.hour, now.minute, now.second)

  configurations = GamblingConfiguration.objects.select_related().filter(
    days_of_week__contains=weekday,
    finish_time__lt=timenow,
  )

  for c in configurations:
    import_from_sources(c.gambling, a_date)

def save_past_gambling_results_by_date(a_date):

  weekday = a_date.weekday()

  configurations = GamblingConfiguration.objects.select_related().filter(
    days_of_week__contains=weekday
  )

  for c in configurations:
    import_from_sources(c.gambling, a_date)

def import_from_sources(gambling, a_date):
  
  any_gambling_result = GamblingResult.objects.filter(gambling=gambling, date=a_date, verified=True)

  if not any_gambling_result:
    for source in (s for s in sources if s.accepts(gambling)):
      already_imported = ImportEvent.objects.filter(source=source.name, gambling=gambling, date=a_date)
      if not already_imported:
        source.import_results(gambling, a_date)
    
    verify_from_sources(gambling, a_date)

  
def verify_from_sources(gambling, a_date):

  results = GamblingResult.objects.filter(gambling=gambling, date=a_date)

  if results:
    gambling_result = results[0]
  else:
    gambling_result = GamblingResult()
    gambling_result.gambling = gambling
    gambling_result.date = a_date

  imported = ImportEvent.objects.filter(gambling=gambling, date=a_date)

  if imported:
    numbers = [i.result_as_list() for i in imported]

    (verified, merged) = merge_results(numbers)
    if merged:
      gambling_result.result = merged
      gambling_result.verified = verified
      gambling_result.save()

      if gambling_result.verified:
        # anuncio que se verifico el resultado del sorteo
        publish_event('VERIFICACION', "Sorteo %s fecha %s" % (gambling.display_name, a_date))

def merge_results(numbers):
  if len(numbers) == 1:
    return (False, numbers[0])
  else:
    any_difference = False
    result = []
    for i in xrange(20):
      sum = 0.0
      for num in numbers:
        sum += int(num[i])

      media = float(sum) / len(numbers)

      if media == int(numbers[0][i]):
        # si el promedio coincide con el primer resultado, entonces todos coinciden
        result.append(numbers[0][i])
      else:
        # si no busco el que mas se parece
        any_difference = True
        min_diff = 10000
        for num in numbers:
          if min_diff > abs(media - int(num[i])):
            min_diff = abs(media - int(num[i]))
            tmp_ret = num[i]
        result.append(tmp_ret)
    return (not any_difference, result)




if __name__ == '__main__':
  print "######################## IMPORT %s #########################" % datetime.now().isoformat(' ')

  usage = "usage: %prog [--start date --end date]"
  parser = OptionParser(usage=usage)
  parser.add_option('-s', '--start', dest='start', help='fecha desde donde importar (ej. 2012-03-28)')
  parser.add_option('-e', '--end', dest='end', help='fecha hasta donde importar (ej. 2012-03-28)')

  (options, args) = parser.parse_args()

  if options.start or options.end:
    if not (options.start and options.end) :
      print "Error se necesitan las dos fechas para importar"
    else:
      from_date = datetime.strptime(options.start, '%Y-%m-%d').date()
      to_date = datetime.strptime(options.end, '%Y-%m-%d').date()
      for a_date in daterange(from_date, to_date):
        save_past_gambling_results_by_date(a_date)

  else:
    today = date.today()
    save_gambling_results_by_date(today)

