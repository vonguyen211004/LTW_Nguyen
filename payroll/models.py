from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee, Position
from decimal import Decimal


class Payroll(models.Model):
	STATUS_CHOICES = [
		('draft', 'Nháp'),
		('processing', 'Đang xử lý'),
		('approved', 'Đã duyệt'),
		('paid', 'Đã thanh toán'),
		('disabled', 'Đã vô hiệu hóa'),
	]

	name = models.CharField(max_length=100, verbose_name='Tên bảng lương')
	month = models.PositiveIntegerField(verbose_name='Tháng', null=True)
	year = models.PositiveIntegerField(verbose_name='Năm', null=True)
	position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='payrolls', verbose_name='Vị trí')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Trạng thái')
	note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payrolls')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Bảng lương'
		verbose_name_plural = 'Bảng lương'
		ordering = ['-year', '-month']
		unique_together = ['month', 'year', 'position']

	def __str__(self):
		return f"Bảng lương {self.position.name} - {self.month}/{self.year}"

	@property
	def total_gross_salary(self):
		"""Tổng thu nhập trước thuế"""
		return sum(detail.gross_salary for detail in self.payroll_details.all())

	@property
	def total_net_salary(self):
		"""Tổng thực lĩnh"""
		return sum(detail.net_salary for detail in self.payroll_details.all())

	@property
	def total_income_tax(self):
		"""Tổng thuế TNCN"""
		return sum(detail.income_tax for detail in self.payroll_details.all())

	@property
	def total_discipline_amount(self):
		"""Tổng tiền phạt kỷ luật"""
		return sum(detail.discipline_amount for detail in self.payroll_details.all())

	@property
	def total_reward_amount(self):
		"""Tổng tiền khen thưởng"""
		return sum(detail.reward_amount for detail in self.payroll_details.all())


class PayrollDetail(models.Model):
	payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_details')
	employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payroll_details')
	basic_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Lương cơ bản')
	standard_workdays = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='Công chuẩn')
	actual_workdays = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='Công thực tế')
	unpaid_leave = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Nghỉ không lương')
	attendance_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tỷ lệ hưởng')
	gross_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Tổng thu nhập')
	taxable_income = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Thu nhập tính thuế')
	income_tax = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Thuế TNCN')
	discipline_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0,
	                                        verbose_name='Tiền phạt kỷ luật')
	reward_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Tiền khen thưởng')
	deduction_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Khấu trừ khác')
	net_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Thực lĩnh')
	note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Chi tiết lương'
		verbose_name_plural = 'Chi tiết lương'
		ordering = ['employee__last_name', 'employee__first_name']
		unique_together = ['payroll', 'employee']

	def __str__(self):
		return f"{self.employee.full_name} - {self.payroll.name}"

	def save(self, *args, **kwargs):
		# Tính lương theo ngày công
		self.gross_salary = (self.basic_salary * self.attendance_ratio).quantize(Decimal('0'))

		# Tính thuế TNCN
		self.taxable_income = self.employee.calculate_taxable_income(self.gross_salary + self.reward_amount)
		self.income_tax = self.employee.calculate_income_tax(self.gross_salary + self.reward_amount)

		# Tính lương thực lĩnh
		self.net_salary = (
					self.gross_salary + self.reward_amount - self.income_tax - self.discipline_amount - self.deduction_amount).quantize(
			Decimal('0'))

		super().save(*args, **kwargs)


class PayrollAllowance(models.Model):
	"""Phụ cấp trong bảng lương"""
	payroll_detail = models.ForeignKey(PayrollDetail, on_delete=models.CASCADE, related_name='allowances')
	name = models.CharField(max_length=100, verbose_name='Tên phụ cấp')
	amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Số tiền/Tỷ lệ')
	is_percentage = models.BooleanField(default=False, verbose_name='Là phần trăm')
	value = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá trị')

	class Meta:
		verbose_name = 'Phụ cấp'
		verbose_name_plural = 'Phụ cấp'

	def __str__(self):
		return f"{self.name} - {self.payroll_detail.employee.full_name}"

	def save(self, *args, **kwargs):
		if self.is_percentage:
			self.value = (self.payroll_detail.gross_salary * self.amount / 100).quantize(Decimal('0'))
		else:
			self.value = self.amount
		super().save(*args, **kwargs)


class PayrollDeduction(models.Model):
	"""Khấu trừ trong bảng lương"""
	payroll_detail = models.ForeignKey(PayrollDetail, on_delete=models.CASCADE, related_name='deductions')
	name = models.CharField(max_length=100, verbose_name='Tên khấu trừ')
	amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Số tiền/Tỷ lệ')
	is_percentage = models.BooleanField(default=False, verbose_name='Là phần trăm')
	value = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá trị')

	class Meta:
		verbose_name = 'Khấu trừ'
		verbose_name_plural = 'Khấu trừ'

	def __str__(self):
		return f"{self.name} - {self.payroll_detail.employee.full_name}"

	def save(self, *args, **kwargs):
		if self.is_percentage:
			self.value = (self.payroll_detail.gross_salary * self.amount / 100).quantize(Decimal('0'))
		else:
			self.value = self.amount
		super().save(*args, **kwargs)