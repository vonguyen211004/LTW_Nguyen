from django.contrib import admin
from .models import AttendanceSummary, AttendanceRecord

class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'month', 'year', 'position', 'transferred', 'created_by')
    list_filter = ('month', 'year', 'position', 'transferred')
    search_fields = ('name',)
    inlines = [AttendanceRecordInline]

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance_summary', 'standard_work_days', 'normal_work_days', 'rest_work_days', 'unpaid_leave')
    list_filter = ('attendance_summary',)
    search_fields = ('employee__first_name', 'employee__last_name')