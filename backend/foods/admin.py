from django.contrib import admin

from .models import Ingredients, Receipts, Tags

admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(Receipts)
