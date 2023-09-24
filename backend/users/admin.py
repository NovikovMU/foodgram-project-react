from django.contrib import admin

from .models import Follow, User


class UsersAdmin(admin.ModelAdmin):
    list_filter = ('email', 'first_name')


admin.site.register(User, UsersAdmin)
admin.site.register(Follow)
