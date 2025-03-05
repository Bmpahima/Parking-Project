from django.contrib import admin
from .models import parkingAuth,ParkingHistory
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class parkingAuthAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name' ,'license_number','is_active' ,'is_admin')
    search_fields = ('license_number',)
    list_per_page = 17

class ParkingHistoryAdmin(admin.ModelAdmin):
    list_display = ('parking_lot','driver','start_time' ,'end_time')
    search_fields = ('driver__first_name','driver__license_number',"driver__last_name")
    list_per_page = 17


# admin.register(User,UserAdmin)
admin.site.register(parkingAuth, parkingAuthAdmin)
admin.site.register(ParkingHistory,ParkingHistoryAdmin)
