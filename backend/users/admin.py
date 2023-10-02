from django.contrib import admin

from .models import Follow, User


class UsersAdmin(admin.ModelAdmin):
    list_filter = ('email', 'first_name')
    exclude = ('password',)


admin.site.register(User, UsersAdmin)
admin.site.register(Follow)
