from django.contrib import admin

from .models import Question, Choice, Laudo, Posto

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Laudo)
admin.site.register(Posto)
