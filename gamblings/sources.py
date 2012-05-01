from gamblings.models import ImportEvent
from datetime import datetime, timedelta
from mofiloterias import now, today

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
      import_event.gambling_name = gambling.name
      import_event.result = numbers
      import_event.save()

      publish_event("Se importo %s fecha %s desde Notitimba" % (gambling.display_name, a_date))

    else:
      print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en Notitimba"



loteriasmundiales_gambling_name_mapping = {
  'prim_prov': ('LP', 0, 'BUENOS AIRES'),
  'prim_nac': ('LN', 0, 'NACIONAL'),
  'prim_stafe': ('L15', 0, 'SANTA FE'),
  'mat_prov': ('LP', 2, 'BUENOS AIRES'),
  'mat_nac': ('LN', 2, 'NACIONAL'),
  'mat_mont': ('L11', 0, 'URUGUAYA'),
  'mat_stafe': ('L15', 3, 'SANTA FE'),
  'vesp_prov': ('LP', 5, 'BUENOS AIRES'),
  'vesp_nac': ('LN', 5, 'NACIONAL'),
  'vesp_stafe': ('L15', 7, 'SANTA FE'),
  'noct_prov': ('LP', 7, 'BUENOS AIRES'),
  'noct_nac': ('LN', 7, 'NACIONAL'),
  'noct_mont': ('L11', 1, 'URUGUAYA'),
  'noct_stafe': ('L15', 10, 'SANTA FE'),
  'noct_cord': ('L6', 9, 'CORDOBA'),
  'noct_sant': ('L17', 4, 'SANTIAGO'),
  'noct_mend': ('L9', 2, 'MENDOZA'),
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


    regex_table = r"<table width=\"180\".*?</table>"

    all_results = re.findall(regex_table, page)

    if len(all_results) > conf[1]:

      table_result = all_results[conf[1]]

      if not conf[2] in table_result:
        print "Se encontro la tabla para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en LoteriasMundiales, pero no coincidia el nombre"

      regex_numbers = r">(\d{3,5})<"

      matches = re.findall(regex_numbers, table_result)

      if len(matches) == 20:
        numbers = []
        for i in xrange(10):
          numbers.append(matches[i*2][1])
        for i in xrange(10):
          numbers.append(matches[i*2+1][1])

        if 'mont' in gambling.name:
          numbers = map(lambda n: n[-3:], numbers)
        else:
          numbers = map(lambda n: n[-4:], numbers)

        import_event = ImportEvent()
        import_event.source = self.name
        import_event.url = 'Not available'
        import_event.date = a_date
        import_event.gambling_name = gambling.name
        import_event.result = numbers
        import_event.save()

        publish_event("Se importo %s fecha %s desde LoteriasMundiales" % (gambling.display_name, a_date))

      else:
        print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en LoteriasMundiales"
    else:
      print "No se encontraron resultados para", gambling.display_name.encode('utf-8'), "fecha", a_date, "en LoteriasMundiales"




