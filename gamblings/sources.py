# coding: utf-8
from gamblings.models import ImportEvent
from datetime import datetime, timedelta
from mofiloterias import now, today, publish_event

import urllib, re

# para notitimba
notitimba_gambling_name_mapping = {
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

class NotitimbaSource:

  def __init__(self):
    self.name = "Notitimba"

  def accepts(self, gambling):
    return notitimba_gambling_name_mapping.get(gambling.name) != None

  def import_results(self, gambling, a_date):
    print "Descargando el sorteo", gambling.display_name.encode('utf-8'), "de la fecha", a_date, "desde Notitimba"
    
    url = "http://www.notitimba.com/quiniela/premios.php?fch=%s&lot=%s" % (a_date, notitimba_gambling_name_mapping[gambling.name])
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

      import_event = ImportEvent()
      import_event.source = self.name
      import_event.url = url
      import_event.date = a_date
      import_event.gambling = gambling
      import_event.result = numbers
      import_event.save()

      publish_event("Se importo %s fecha %s desde Notitimba" % (gambling.display_name, a_date))

    else:
      print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en Notitimba"



loteriasmundiales_gambling_name_mapping = {
  'prim_prov': ('LN', 'BUENOS AIRES (11:30 hs.)'),
  'prim_nac': ('LN', 'NACIONAL (11:30 hs.)'),
  'prim_stafe': ('L15', 'SANTA FE (11:30 hs.)'),
  'mat_prov': ('LN', 'BUENOS AIRES (14:00 hs.)'),
  'mat_nac': ('LN', 'NACIONAL (14:00 hs.)'),
  'mat_mont': ('LN', 'URUGUAYA (14:00 hs.)'),
  'mat_stafe': ('L15', 'SANTA FE (14:00 hs.)'),
  'vesp_prov': ('LN', 'BUENOS AIRES (17:30 hs.)'),
  'vesp_nac': ('LN', 'NACIONAL (17:30 hs.)'),
  'vesp_stafe': ('L15', 'SANTA FE (17:30 hs.)'),
  'noct_prov': ('LN', 'BUENOS AIRES (21:00 hs.)'),
  'noct_nac': ('LN', 'NACIONAL (21:00 hs.)'),
  'noct_mont': ('L11', 'URUGUAYA (20:00 hs.)'),
  'noct_stafe': ('L15', 'SANTA FE (21:00 hs.)'),
  'noct_cord': ('L6', 'CORDOBA (21:10 hs.)'),
  'noct_sant': ('L17', 'SANTIAGO (22:30 hs)'),
  'noct_mend': ('L9', 'MENDOZA (21:00 hs.)'),
}

loteriasmundiales_month_mapping = {
  1: 'enero',
  2: 'febrero',
  3: 'marzo',
  4: 'abril',
  5: 'mayo',
  6: 'junio',
  7: 'julio',
  8: 'agosto',
  9: 'septiembre',
  10: 'octubre',
  11: 'noviembre',
  12: 'diciembre',
}

class LoteriasMundialesSource:

  def __init__(self):
    self.name = "LoteriasMundiales"

  def accepts(self, gambling):
    return loteriasmundiales_gambling_name_mapping.get(gambling.name) != None

  def import_results(self, gambling, a_date):
    print "Descargando el sorteo", gambling.display_name.encode('utf-8'), "de la fecha", a_date, "desde LoteriasMundiales"
    conf = loteriasmundiales_gambling_name_mapping[gambling.name]

    url = "http://www.loteriasmundiales.com.ar/index.asp"
    params = urllib.urlencode({
      'cDia': a_date.day, 
      'cMes': a_date.month, 
      'cAno': a_date.year, 
      'pagina': conf[0]
    })
    f = urllib.urlopen(url, params)
    page = f.read()

    regex_date = r"sTitulo.innerHTML='RESULTADOS DEL.*"

    page_date = re.search(regex_date, page)
    day = a_date.day if a_date.day > 9 else "0%s" % a_date.day
    month = loteriasmundiales_month_mapping[a_date.month]
    year = a_date.year

    expected_date = "%s de %s de %s" % (day, month, year)


    if not page_date or page_date.group(0).lower().find(expected_date) < 0:
      print "No coinciden las fechas para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en LoteriasMundiales."
      return None

    regex_table = r"<table width=\"180\".*?</table>"

    all_results = re.findall(regex_table, page)

    for table_result in all_results:
      if conf[1] in table_result:

        regex_numbers = r">(\d{3,5})<"

        matches = re.findall(regex_numbers, table_result)

        if len(matches) == 20:
          numbers = []
          for i in xrange(10):
            numbers.append(matches[i*2])
          for i in xrange(10):
            numbers.append(matches[i*2+1])

          if 'mont' in gambling.name:
            numbers = map(lambda n: n[-3:], numbers)
          else:
            numbers = map(lambda n: n[-4:], numbers)

          print "Resultado encontrado para",gambling.display_name.encode('utf-8'),"fecha", a_date, ":", numbers
          import_event = ImportEvent()
          import_event.source = self.name
          import_event.url = 'Not available'
          import_event.date = a_date
          import_event.gambling = gambling
          import_event.result = numbers
          import_event.save()

          publish_event("Se importo %s fecha %s desde LoteriasMundiales" % (gambling.display_name, a_date))

        else:
          print "Se encontro la tabla para", gambling.display_name.encode('utf-8'), "fecha", a_date, ", pero no los 20 numeros en LoteriasMundiales"

        return None

    print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en LoteriasMundiales"



