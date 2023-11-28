from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class original_audio(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    code = models.CharField(max_length=20)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Processed(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    original_file = models.FileField()
    processed_file = models.FileField(null=True, blank=True)
    Transcript= models.TextField()
    Mood = models.CharField(max_length=500, null=True, blank=True)
    Satisfaction = models.CharField(max_length=100, null=True, blank=True)
    DetailsShared = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Meta:
    app_label = 'auditor_app'