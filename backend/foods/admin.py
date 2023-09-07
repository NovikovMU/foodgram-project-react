from django.contrib import admin

from .models import Ingredients, Receipts, Tags, ReceiptsIngredients, ReceiptsTags

admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(Receipts)
admin.site.register(ReceiptsIngredients)
admin.site.register(ReceiptsTags)
