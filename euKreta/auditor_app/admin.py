from django.contrib import admin

# Register your models here.
from .models import original_audio, Processed
# from .models import  Processed

admin.site.register(original_audio)
admin.site.register(Processed)