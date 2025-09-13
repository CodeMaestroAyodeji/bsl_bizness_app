from django.contrib import admin
from .models import Vendor, Profile
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


# Register your models here.
# admin.site.register(Vendor)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
