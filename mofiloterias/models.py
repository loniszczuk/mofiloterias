from django.db import models

class Event(models.Model):
  datetime = models.DateTimeField(auto_now_add=True)
  description = models.CharField(max_length=512)

  def __str__(self):
    return str(self.datetime.strftime('%H:%M:%S')) + "::" + str(self.description.encode('utf-8'))
  