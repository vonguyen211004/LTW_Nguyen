from django.contrib import admin
from .models import Payroll, PayrollDetail, PayrollAllowance






class PayrollAllowanceInline(admin.TabularInline):
	model = PayrollAllowance
	extra = 0


class PayrollDetailInline(admin.TabularInline):
	model = PayrollDetail
	extra = 0
	show_change_link = True


@admin.register(PayrollDetail)
class PayrollDetailAdmin(admin.ModelAdmin):
	list_display = ('employee', 'payroll', 'basic_salary', 'gross_salary', 'net_salary')
	list_filter = ('payroll',)
	search_fields = ('employee__full_name', 'employee__code')
	inlines = [ PayrollAllowanceInline]

