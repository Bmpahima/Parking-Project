from django.contrib import admin
from .models import ParkingLot,Parking
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class ParkingLotAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id')  # חיפוש לפי שם חניון או מזהה
    list_display = ('id', 'name', 'parking_spots', 'payment')  # שדות שיוצגו בטבלה הראשית
    list_filter = ('payment',)  # סינון לפי האם יש תשלום
    ordering = ('name',)  # מיון לפי שם החניון

class ParkingAdmin(admin.ModelAdmin):
    list_display = ('parking_lot', 'occupied')
    search_fields = ('driver','id','license_number')

# admin.register(User,UserAdmin)
admin.site.register(ParkingLot, ParkingLotAdmin)
admin.site.register(Parking, ParkingAdmin)