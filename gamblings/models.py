from django.db import models
import json

class Gambling(models.Model):
  name = models.CharField(max_length=30, unique=True)
  display_name = models.CharField(max_length=100)

class GamblingResult(models.Model):

  gambling = models.ForeignKey('Gambling')
  date = models.DateField()
  result = models.CommaSeparatedIntegerField(max_length=200)
  verified = models.BooleanField()

  def result_as_list(self):
    return map(lambda x: x.encode('utf-8'), self.result.replace("'", '').replace(' ','')[1:-1].split(','))

class GamblingConfiguration(models.Model):

  gambling = models.ForeignKey('Gambling')

  # dias_sorteo es una lista de enteros que representan que dias se juega este sorteo
  # 0:lun, 1:mar, 2:mie, 3:jue, 4:vie, 5:sab, 6:dom
  days_of_week = models.CommaSeparatedIntegerField(max_length=20)
  time = models.TimeField()
  finish_time = models.TimeField()

  def __str__(self):
    return "%s(%s)" % (self.display_name, self.name)

class GamblingSummary(models.Model):

  name = models.CharField(max_length=30)
  # 0:lun, 1:mar, 2:mie, 3:jue, 4:vie, 5:sab, 6:dom
  days_of_week = models.CommaSeparatedIntegerField(max_length=50)
  gamblings = models.ManyToManyField('Gambling')

class ImportEvent(models.Model):
  source = models.CharField(max_length=100)
  url = models.CharField(max_length=100)
  date = models.DateField()
  gambling = models.ForeignKey('Gambling')
  result = models.CommaSeparatedIntegerField(max_length=200)

  def result_as_list(self):
    return map(lambda x: x.encode('utf-8'), self.result.replace("'", '').replace(' ','')[1:-1].split(','))