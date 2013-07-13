import mofiloterias.settings
from mofiloterias import publish_event
from gamblings.models import GamblingConfiguration, GamblingResult, ImportEvent
from datetime import date, datetime, time

import pika, json, sys, logging

from gamblings.sources import *

logger = logging.getLogger("gamblings.import_worker")

sources = [
  NotitimbaSource(),
  ViviTuSuerteSource(),
  LoteriasMundialesSource()
]

def import_from_sources(gambling, a_date):
  
  any_gambling_result = GamblingResult.objects.filter(gambling=gambling, date=a_date, verified=True)

  if not any_gambling_result:
    logger.info("*******************************************")
    for source in (s for s in sources if s.accepts(gambling)):
      already_imported = ImportEvent.objects.filter(source=source.name, gambling=gambling, date=a_date)
      if not already_imported:
        source.import_results(gambling, a_date)
    logger.info("*******************************************")
    
    verify_from_sources(gambling, a_date)

  
def verify_from_sources(gambling, a_date):
  logger.info("Chequeando verificacion")

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
        logger.info("Se verificaron los resultados del sorteo %s fecha %s" % (gambling.name, a_date))
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
  gambling_to_import = json.loads(body)
  try: 

    a_date = datetime.strptime(gambling_to_import['date'], '%Y-%m-%d').date() 
    gambling_name = gambling_to_import['name']

    logger.info("Mensaje recibido: Sorteo %s; Fecha %s" % (gambling_name, a_date))

    configurations = GamblingConfiguration.objects.select_related().filter(
      days_of_week__contains=a_date.weekday(),
      gambling__name=gambling_name,
    )
    if configurations:
      logger.info("Configuracion valida. Importando: Sorteo %s; Fecha %s" % (gambling_name, a_date))
      configuration = configurations[0]
      import_from_sources(configuration.gambling, a_date)
    else:
      logger.info("No existe una configuracion para el sorteo %s en la fecha %s" % (gambling_name, a_date))
      pass

  except:
     logger.error("Unexpected error: %s" % sys.exc_info()[0])
     retries = gambling_to_import['retries']
     if retries < 3 :
        gambling_to_import['retries'] = retries + 1
        message = json.dumps(gambling_to_import)
        ch.basic_publish(exchange='',
          routing_key='import_gamblings',
          body=message,
          properties=pika.BasicProperties(
           delivery_mode = 2, # make message persistent
          )
        )


  ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == '__main__':

  logger.info("Starting Import Worker")

  connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.queue_declare(queue='import_gamblings', durable=True)

  channel.basic_qos(prefetch_count=1)
  channel.basic_consume(import_callback, queue='import_gamblings')

  channel.start_consuming()
