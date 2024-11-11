from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'last_login',
        'is_active',
        'join_date'
    )
    list_display_links = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    ordering = ('-join_date',)
    readonly_fields = ('last_login','join_date',)
    filter_horizontal =()
    list_filter =()
    fieldsets = ()
admin.site.register(Account,AccountAdmin)