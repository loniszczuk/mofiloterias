from django.db import models

class Event(models.Model):
  title = models.CharField(max_length=128)
  description = models.CharField(max_length=512)
  time = models.IntegerField()

  def to_dict(self):
    return {'title': self.title, 'description': self.description, 'time': self.time}