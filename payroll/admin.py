from django.contrib import admin
from .models import Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction

class PayrollDetailInline(admin.TabularInline):
    model = PayrollDetail
    extra = 0

class PayrollAllowanceInline(admin.TabularInline):
    model = PayrollAllowance
    extra = 0

class PayrollDeductionInline(admin.TabularInline):
    model = PayrollDeduction
    extra = 0

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('name', 'month', 'year', 'position', 'status', 'created_by')
    list_filter = ('month', 'year', 'position', 'status')
    search_fields = ('name',)
    inlines = [PayrollDetailInline]

@admin.register(PayrollDetail)
class PayrollDetailAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll', 'basic_salary', 'attendance_ratio', 'gross_salary', 'net_salary')
    list_filter = ('payroll',)
    search_fields = ('employee__first_name', 'employee__last_name')
    inlines = [PayrollAllowanceInline, PayrollDeductionInline]