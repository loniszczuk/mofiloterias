import mofiloterias.settings
from gamblings.models import GamblingConfiguration, GamblingResult
from datetime import date, datetime, time

import pika, json

def submit_gambling_import_by_date(a_date, rabbit_channel):

  weekday = a_date.weekday()
  now = datetime.now()
  timenow = time(now.hour, now.minute, now.second)

  if a_date < date.today():
    configurations = GamblingConfiguration.objects.select_related().filter(
      days_of_week__contains=weekday,
    )
  else:
    configurations = GamblingConfiguration.objects.select_related().filter(
      days_of_week__contains=weekday,
      finish_time__lt=timenow,
    )

  for c in configurations:

    any_gambling_result = GamblingResult.objects.filter(gambling=c.gambling, date=a_date, verified=True)

    if not any_gambling_result:
      message = json.dumps({'date': a_date.isoformat(), 'name': c.gambling.name})

      print "publish"
      rabbit_channel.basic_publish(exchange='',
        routing_key='import_gamblings',
        body=message,
        properties=pika.BasicProperties(
         delivery_mode = 2, # make message persistent
       )
     )

if __name__ == '__main__':
  
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.queue_declare(queue='import_gamblings', durable=True)

  submit_gambling_import_by_date(date.today(), channel)



