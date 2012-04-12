from optparse import OptionParser
from gamblings.models import GamblingConfiguration, GamblingResult
from mofiloterias.models import Event
from datetime import date, tzinfo, datetime, timedelta, time
import urllib, re


# para notitimba
gambling_name_mapping = {
  'prim_prov':0,
  'prim_nac':1,
  'prim_stafe':16,
  'mat_prov':2,
  'mat_prov_sab':2,
  'mat_nac':3,
  'mat_nac_sab':3,
  'mat_mont':8,
  'mat_stafe':14,
  'mat_stafe_sab':14,
  'vesp_prov':4,
  'vesp_nac':5,
  'vesp_stafe':15,
  'noct_prov':6,
  'noct_nac':7,
  'noct_mont':9,
  'noct_stafe':13,
  'noct_cord':10,
  'noct_sant':11,
  'noct_mend':12,
}

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

def save_gambling_results_by_date(a_date):

  weekday = a_date.weekday()
  now = datetime.now()
  timenow = time(now.hour, now.minute, now.second)

  configurations = GamblingConfiguration.objects.select_related().filter(
    days_of_week__contains=weekday,
    finish_time__lt=timenow
  )

  for c in configurations:
    save_gambling_result(c.gambling, a_date)

def save_past_gambling_results_by_date(a_date):

  weekday = a_date.weekday()

  configurations = GamblingConfiguration.objects.select_related().filter(
    days_of_week__contains=weekday
  )

  for c in configurations:
    save_gambling_result(c.gambling, a_date)



def save_gambling_result(gambling, a_date):
  
  s = GamblingResult.objects.filter(gambling=gambling, date=a_date)
  if not s:
    save_from_notitimba(gambling, a_date)


def save_from_notitimba(gambling, a_date):
  print "Descargando el sorteo", gambling.display_name.encode('utf-8'), "de la fecha", a_date, "desde Notitimba"
  
  url = "http://www.notitimba.com/quiniela/premios.php?fch=%s&lot=%s" % (a_date, gambling_name_mapping[gambling.name])
  f = urllib.urlopen(url)

  page = f.read()

  if 'mont' in gambling.name:
    regex = r"<td>(<font color=red><b>)?\s(\d{3})</td>"
  else:
    regex = r"<td>(<font color=red><b>)?(\d{4})</td>"

  matches = re.findall(regex, page)
  if len(matches) == 20:
    numbers = []
    for i in xrange(10):
      numbers.append(matches[i*2][1])
    for i in xrange(10):
      numbers.append(matches[i*2+1][1])

    print "Resultado encontrado para",gambling.display_name.encode('utf-8'),"fecha", a_date, ":", numbers

    s = GamblingResult()
    s.gambling = gambling
    s.date = a_date
    s.result = numbers
    s.save()

    e = Event()
    e.description = "Se importo %s fecha %s" % (gambling.display_name, a_date)
    e.save()

  else:
    print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date


if __name__ == '__main__':
  print "######################## IMPORT %s #########################" % datetime.now().isoformat(' ')

  usage = "usage: %prog [--from date --to date]"
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




