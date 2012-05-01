import mofiloterias.settings
from mofiloterias.models import Event
from datetime import datetime
from pytz import timezone


def now():
  return datetime.now(timezone(settings.TIME_ZONE)).time()

def today():
  return datetime.now(timezone(settings.TIME_ZONE)).date()

def publish_event(description):
  e = Event()
  e.description = description
  e.save()