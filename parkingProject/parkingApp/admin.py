from django.contrib import admin
from .models import ParkingLot,Parking
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')

class ParkingLotAdmin(admin.ModelAdmin):
    """
    Admin interface for the ParkingLot model.

    Features:
    - search_fields: Enables admin users to search parking lots by name or ID.
    - list_display: Displays the ID, name, number of parking spots, and payment details in the list view.
    - ordering: Sorts the list view entries by ID.
    - list_per_page: Limits the list view to 17 entries per page for better pagination.
    - filter_horizontal: Provides a horizontal multi-select widget for assigning multiple owners.
    """
    search_fields = ('name', 'id')
    list_display = ('id', 'name', 'parking_spots', 'payment')
    ordering = ('id',) #sort by name of the parking lot
    list_per_page = 17
    filter_horizontal = ("owner",) 


class ParkingAdmin(admin.ModelAdmin):
    """
    Admin interface for the Parking model.

    Features:
    - list_display: Shows the parking spot ID, related parking lot, whether it's occupied, and whether it's reserved.
    - search_fields: Allows admin users to search by driver name, parking ID, or license plate number.
    """
    
    list_display = ('id','parking_lot', 'occupied', 'is_saved')
    search_fields = ('driver','id','license_number')



# admin.register(User,UserAdmin)
admin.site.register(ParkingLot, ParkingLotAdmin)
admin.site.register(Parking, ParkingAdmin)