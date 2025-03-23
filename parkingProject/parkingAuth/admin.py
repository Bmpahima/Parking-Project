from django.contrib import admin
from .models import parkingAuth, ParkingHistory

class parkingAuthAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'license_number', 'is_active', 'is_admin')
    search_fields = ('license_number',)
    list_per_page = 17

class ParkingHistoryAdmin(admin.ModelAdmin):
    list_display = ('parking_lot', 'driver', 'start_time', 'end_time')
    search_fields = ('driver__first_name', 'driver__license_number', 'driver__last_name')
    list_per_page = 17
    actions = ['delete_all_history']  # הוספת הפעולה לרשימה

    @admin.action(description="🗑️ Delete ALL parking history records")
    def delete_all_history(self, request, queryset):
        ParkingHistory.objects.all().delete()
        self.message_user(request, "All parking history records were deleted successfully.")

admin.site.register(parkingAuth, parkingAuthAdmin)
admin.site.register(ParkingHistory, ParkingHistoryAdmin)
