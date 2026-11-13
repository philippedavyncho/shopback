from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address
admin.site.register(User, UserAdmin)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin): list_display = ("recipient_name", "user", "city", "country"); search_fields = ("recipient_name", "user__email", "city")
