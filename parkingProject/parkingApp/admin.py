from django.contrib import admin
from .models import User,ParkingLot,Parking

class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'lisence_number')
    search_fields = ('lisence_number')


class ParkingLotAdmin(admin.ModelAdmin):
    pass

class ParkingAdmin(admin.ModelAdmin):
    list_display = ('parking_lot', 'disabled_parking', 'occupied')

admin.register(User,UserAdmin)
admin.register(ParkingLot)
admin.register(Parking,ParkingAdmin)