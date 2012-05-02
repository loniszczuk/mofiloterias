from django.db import models

class Event(models.Model):
  title = models.CharField(max_length=128)
  description = models.CharField(max_length=512)

  def __str__(self):
    return str(self.title.encode('utf-8') + ':' + self.description.encode('utf-8'))
  