from django.contrib import admin
from .models import parkingAuth
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class parkingAuthAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name' ,'license_number','is_active' ,'is_admin')
    search_fields = ('license_number',)
    list_per_page = 17

# admin.register(User,UserAdmin)
admin.site.register(parkingAuth, parkingAuthAdmin)
