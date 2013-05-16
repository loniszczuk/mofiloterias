import mofiloterias.settings
from mofiloterias import publish_event
from gamblings.models import GamblingConfiguration, GamblingResult, ImportEvent
from datetime import date, datetime, time

import pika, json, sys

from gamblings.sources import *

sources = [
  NotitimbaSource(),
  LoteriasMundialesSource(),
  ViviTuSuerteSource()
]

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


def import_callback(ch, method, properties, body):
  try: 
    gambling_to_import = json.loads(body)

    a_date = datetime.strptime(gambling_to_import['date'], '%Y-%m-%d').date() 
    gambling_name = gambling_to_import['name']

    print "importing", gambling_name, a_date

    configuration = GamblingConfiguration.objects.select_related().get(
      days_of_week__contains=a_date.weekday(),
      gambling__name=gambling_name,
    )

    import_from_sources(configuration.gambling, a_date)

    ch.basic_ack(delivery_tag = method.delivery_tag)
  except:
     print "Unexpected error:", sys.exc_info()[0]


if __name__ == '__main__':

  print "########## Starting Import Worker %s ##########" % datetime.now().isoformat(' ')

  connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.queue_declare(queue='import_gamblings', durable=True)

  channel.basic_qos(prefetch_count=1)
  channel.basic_consume(import_callback, queue='import_gamblings')

  channel.start_consuming()
