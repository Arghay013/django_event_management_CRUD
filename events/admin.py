from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import Event, Category

# Register your models here.
admin.site.register(Event)
admin.site.register(Category)

# Customize User admin to show groups
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('groups', 'is_staff', 'is_superuser', 'is_active')
    
    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize Group admin
admin.site.unregister(Group)
admin.site.register(Group)
