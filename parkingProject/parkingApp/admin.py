from django.contrib import admin
from .models import ParkingLot,Parking
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class ParkingLotAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id')  # חיפוש לפי שם חניון או מזהה
    list_display = ('id', 'name', 'parking_spots', 'payment')  # שדות שיוצגו בטבלה הראשית
    ordering = ('id',)  # מיון לפי שם החניון
    list_per_page = 17
    filter_horizontal = ("owner",) 


class ParkingAdmin(admin.ModelAdmin):
    list_display = ('id','parking_lot', 'occupied')
    search_fields = ('driver','id','license_number')



# admin.register(User,UserAdmin)
admin.site.register(ParkingLot, ParkingLotAdmin)
admin.site.register(Parking, ParkingAdmin)