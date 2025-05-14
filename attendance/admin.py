from django.contrib import admin
from .models import WorkShift, AttendanceRecord

@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'start_time', 'end_time')
    search_fields = ('name', 'code')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'attendance_type')
    list_filter = ('start_date', 'end_date', 'attendance_type')
    search_fields = ('name',)