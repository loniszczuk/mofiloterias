# coding: utf-8
from gamblings.models import ImportEvent
from datetime import datetime, timedelta
from mofiloterias import now, today, publish_event

import urllib, re, logging

logger = logging.getLogger("gamblings.sources")

# para notitimba
notitimba_gambling_name_mapping = {
  'prim_prov':0,
  'prim_nac':4,
  'prim_stafe':10,
  'mat_prov':1,
  'mat_nac':5,
  'mat_mont':8,
  'mat_stafe':11,
  'vesp_prov':2,
  'vesp_nac':6,
  'vesp_stafe':12,
  'noct_prov':3,
  'noct_nac':7,
  'noct_mont':9,
  'noct_stafe':13,
  'noct_cord':15,
  'noct_sant':16,
  'noct_mend':14,
}

class NotitimbaSource:

  def __init__(self):
    self.name = "Notitimba"

  def accepts(self, gambling):
    return notitimba_gambling_name_mapping.get(gambling.name) != None

  def import_results(self, gambling, a_date):
    try:
      logger.info("*******************************************************") 
      logger.info("Descargando el sorteo %s de la fecha %s desde Notitimba" % (gambling.display_name, a_date))
    
      url = "http://www.notitimba.com/loterias/premios.php?a=%s&b=%s" % (a_date, notitimba_gambling_name_mapping[gambling.name])
      logger.info("Url : %s" % url)
    
      f = urllib.urlopen(url)
      page = f.read()

      if !page.startswith("|"):
        digits = min(4, int(page[0]))
        numbers = []

        for i in xrange(20):
          idx = 1 + 6*i
          numbers.append(page[idx+6-digits:idx+6])

        logger.info("Resultado encontrado: %s" % numbers)

        import_event = ImportEvent()
        import_event.source = self.name
        import_event.url = url
        import_event.date = a_date
        import_event.gambling = gambling
        import_event.result = numbers
        import_event.save()

        publish_event('IMPORTACION', "sorteo %s fecha %s desde Notitimba" % (gambling.display_name, a_date))

      else:
        logger.info("Resultado NO encontrado")
    except: 
      logger.error("Error en LoteriasMundiales: %s" % sys.exc_info()[0])



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
    try:
      logger.info("*******************************************************")
      logger.info("Descargando el sorteo %s de la fecha %s desde LoteriasMundiales" % (gambling.display_name, a_date))
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
        logger.info("No coinciden las fechas. Fecha de la pagina: %s ; Fecha esperada: %s" % (page_date, expected_date) )
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

            logger.info("Resultado encontrado: %s" % numbers)
            import_event = ImportEvent()
            import_event.source = self.name
            import_event.url = 'Not available'
            import_event.date = a_date
            import_event.gambling = gambling
            import_event.result = numbers
            import_event.save()

            publish_event('IMPORTACION', "sorteo %s fecha %s desde LoteriasMundiales" % (gambling.display_name, a_date))
          else:
            logger.info("Se encontro la tabla pero no los 20 numeros")
          return None

      logger.info("Resultado NO encontrado")
    except: 
      logger.error("Error en LoteriasMundiales: %s" % sys.exc_info()[0])

vivitusuerte_gambling_name_mapping = {
  'prim_prov': (24, 'Provincia - La Primera'),
  'prim_nac': (25, 'Nacional - La Primera'),
  'prim_stafe': (38, 'Santa Fe - La Primera'),
  'mat_prov': (24, 'Provincia - Matutino'),
  'mat_nac': (25, 'Nacional - Matutino'),
  'mat_mont': (23, 'Montevideo - Matutino'),
  'mat_stafe': (38, 'Santa Fe - Matutino'),
  'vesp_prov': (24, 'Provincia - Vespertino'),
  'vesp_nac': (25, 'Nacional - Vespertino'),
  'vesp_stafe': (38, 'Santa Fe - Vespertino'),
  'noct_prov': (24, 'Provincia - Nocturna'),
  'noct_nac': (25, 'Nacional - Nocturna'),
  'noct_mont': (23, 'Montevideo - Nocturna'),
  'noct_stafe': (38, 'Santa Fe - Nocturna'),
  'noct_cord': (28, 'rdoba - Nocturna'),
  'noct_sant': (48, 'Santiago - Nocturna'),
  'noct_mend': (53, 'Mendoza - Nocturna'),
}
class ViviTuSuerteSource:

  def __init__(self):
    self.name = "ViviTuSuerte"

  def accepts(self, gambling):
    return vivitusuerte_gambling_name_mapping.get(gambling.name) != None

  def import_results(self, gambling, a_date):
    try:
      logger.info("*******************************************************")
      logger.info("Descargando el sorteo %s de la fecha %s desde ViviTuSuerte" % (gambling.display_name, a_date) )
    
      conf = vivitusuerte_gambling_name_mapping[gambling.name]

      url = "http://www.vivitusuerte.com/datospizarra_loteria.php"
      params = urllib.urlencode({
        'fecha': a_date.strftime('%Y/0%m/0%d'),
        'loteria': conf[0]
      })

      f = urllib.urlopen(url, params)
      lines = f.readlines()

      table_found = False
      numbers_found = 0
      numbers_tmp = [[],[]]
      numbers = []
      regex_number = r'>(\d{3,5})<'

      for l in lines:

        if not table_found:
          # busco el encabezado de la tabla que me interesa
          if conf[1] in l:
            table_found = True
        else:
          # busco los numeros
          match = re.search(regex_number, l)

          if match and match.group(1):
            i = numbers_found % 2
            numbers_tmp[i].append(match.group(1))

            numbers_found += 1

            if numbers_found == 20:
              numbers = numbers_tmp[0] + numbers_tmp[1]
              break

      if len(numbers) == 20:
        if 'mont' in gambling.name:
          numbers = map(lambda n: n[-3:], numbers)
        else:
          numbers = map(lambda n: n[-4:], numbers)

        logger.info("Resultado encontrado: %s" % numbers)
        import_event = ImportEvent()
        import_event.source = self.name
        import_event.url = 'Not available'
        import_event.date = a_date
        import_event.gambling = gambling
        import_event.result = numbers
        import_event.save()

        publish_event('IMPORTACION', "sorteo %s fecha %s desde ViviTuSuerte" % (gambling.display_name, a_date))
      else:
        logger.info("Resultado NO encontrado")

    except: 
      logger.error("Error en ViviTuSuerte: %s" % sys.exc_info()[0])

