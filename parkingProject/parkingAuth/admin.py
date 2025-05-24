from django.contrib import admin
from .models import parkingAuth, ParkingHistory

class parkingAuthAdmin(admin.ModelAdmin):
    """
    Customizes the Django admin interface for the `parkingAuth` model.

    Features:
        - Displays key driver details in the list view.
        - Enables search by license number.
        - Paginates the list view to show 17 entries per page.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields that are searchable.
        list_per_page (int): Number of records per page.
    """

    list_display = ('first_name', 'last_name', 'license_number', 'is_active', 'is_admin')
    search_fields = ('license_number',)
    list_per_page = 17

class ParkingHistoryAdmin(admin.ModelAdmin):
    """
    Customizes the Django admin interface for the `ParkingHistory` model.

    Features:
        - Displays parking event details.
        - Enables search by driver name or license number.
        - Adds a custom admin action to delete all parking history.
        - Paginates the list view to show 17 entries per page.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields that are searchable (supports foreign key lookups).
        list_per_page (int): Number of records per page.
        actions (list): Custom actions available in the admin.
    """
    
    list_display = ('parking', 'driver', 'start_time', 'end_time')
    search_fields = ('driver__first_name', 'driver__license_number', 'driver__last_name')
    list_per_page = 17
    actions = ['delete_all_history']  #Adding the action to the list

    @admin.action(description="🗑️ Delete ALL parking history records")
    def delete_all_history(self, request, queryset):
        ParkingHistory.objects.all().delete()
        self.message_user(request, "All parking history records were deleted successfully.")

admin.site.register(parkingAuth, parkingAuthAdmin)
admin.site.register(ParkingHistory, ParkingHistoryAdmin)
