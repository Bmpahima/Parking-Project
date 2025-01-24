from django.contrib import admin
from .models import parkingAuth
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class parkingAuthAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name' ,'is_active' ,'is_admin')
    

# admin.register(User,UserAdmin)
admin.site.register(parkingAuth, parkingAuthAdmin)
