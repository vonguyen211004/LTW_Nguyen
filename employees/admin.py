from django.contrib import admin
from .models import Position, Employee, Dependent, Discipline, Reward


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')
	search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ('code', 'full_name', 'position', 'phone', 'is_active')
	list_filter = ('position', 'is_active', 'gender')
	search_fields = ('code', 'first_name', 'last_name', 'phone', 'email')
	fieldsets = (
		('Thông tin cơ bản', {
			'fields': ('code', 'first_name', 'last_name', 'gender', 'date_of_birth', 'id_number', 'photo')
		}),
		('Thông tin liên hệ', {
			'fields': ('phone', 'email', 'address')
		}),
		('Thông tin công việc', {
			'fields': ('position', 'join_date', 'is_active')
		}),
		('Thông tin học vấn', {
			'fields': ('education_level', 'degree', 'major')
		}),
		('Thông tin lương', {
			'fields': ('basic_salary',)
		}),
		('Thông tin thuế', {
			'fields': ('tax_code', 'tax_exemption', 'dependents')
		}),
	)

	def full_name(self, obj):
		return obj.full_name

	full_name.short_description = 'Họ và tên'


@admin.register(Dependent)
class DependentAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'employee', 'relationship', 'date_of_birth', 'is_active')
	list_filter = ('relationship', 'is_active')
	search_fields = ('full_name', 'employee__first_name', 'employee__last_name')


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
	list_display = ('employee', 'date', 'discipline_type', 'amount', 'created_by')
	list_filter = ('discipline_type', 'date')
	search_fields = ('employee__first_name', 'employee__last_name', 'note')


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
	list_display = ('employee', 'date', 'reward_type', 'amount', 'created_by')
	list_filter = ('reward_type', 'date')
	search_fields = ('employee__first_name', 'employee__last_name', 'note')