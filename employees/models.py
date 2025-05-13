from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Position(models.Model):
	name = models.CharField(max_length=100, verbose_name='Tên vị trí')
	description = models.TextField(blank=True, null=True, verbose_name='Mô tả')

	class Meta:
		verbose_name = 'Vị trí công việc'
		verbose_name_plural = 'Vị trí công việc'
		ordering = ['name']

	def __str__(self):
		return self.name


class Employee(models.Model):
	GENDER_CHOICES = [
		('M', 'Nam'),
		('F', 'Nữ'),
		('O', 'Khác'),
	]

	EDUCATION_LEVEL_CHOICES = [
		('high_school', 'Trung học phổ thông'),
		('college', 'Cao đẳng'),
		('university', 'Đại học'),
		('master', 'Thạc sĩ'),
		('phd', 'Tiến sĩ'),
		('other', 'Khác'),
	]

	# Thông tin cơ bản
	code = models.CharField(max_length=20, unique=True, verbose_name='Mã nhân viên')
	first_name = models.CharField(max_length=50, verbose_name='Tên')
	last_name = models.CharField(max_length=50, verbose_name='Họ')
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Giới tính')
	date_of_birth = models.DateField(verbose_name='Ngày sinh')
	id_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số CMND/CCCD')

	# Thông tin liên hệ
	phone = models.CharField(max_length=15, verbose_name='Số điện thoại')
	email = models.EmailField(blank=True, null=True, verbose_name='Email')
	address = models.TextField(blank=True, null=True, verbose_name='Địa chỉ')

	# Thông tin công việc
	position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='employees', verbose_name='Vị trí')
	join_date = models.DateField(verbose_name='Ngày vào làm')
	is_active = models.BooleanField(default=True, verbose_name='Đang làm việc')

	# Thông tin học vấn
	education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True, null=True,
	                                   verbose_name='Trình độ học vấn')
	degree = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bằng cấp')
	major = models.CharField(max_length=100, blank=True, null=True, verbose_name='Chuyên ngành')

	# Thông tin lương
	basic_salary = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Lương cơ bản')

	# Thông tin thuế
	tax_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Mã số thuế')
	tax_exemption = models.BooleanField(default=False, verbose_name='Miễn thuế')
	dependents = models.PositiveIntegerField(default=0, verbose_name='Số người phụ thuộc')

	# Thông tin khác
	photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True, verbose_name='Ảnh đại diện')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Nhân viên'
		verbose_name_plural = 'Nhân viên'
		ordering = ['last_name', 'first_name']

	def __str__(self):
		return f"{self.code} - {self.full_name}"

	@property
	def full_name(self):
		return f"{self.last_name} {self.first_name}"

	def calculate_personal_deduction(self):
		"""Tính giảm trừ gia cảnh cho bản thân"""
		return Decimal('11000000')  # 11 triệu đồng/tháng

	def calculate_dependent_deduction(self):
		"""Tính giảm trừ gia cảnh cho người phụ thuộc"""
		return Decimal('4400000') * Decimal(str(self.dependents))  # 4.4 triệu đồng/người/tháng

	def calculate_total_deduction(self):
		"""Tính tổng giảm trừ gia cảnh"""
		return self.calculate_personal_deduction() + self.calculate_dependent_deduction()

	def calculate_taxable_income(self, gross_income):
		"""Tính thu nhập chịu thuế"""
		if self.tax_exemption:
			return Decimal('0')

		taxable_income = gross_income - self.calculate_total_deduction()
		return max(taxable_income, Decimal('0'))

	def calculate_income_tax(self, gross_income):
		"""Tính thuế TNCN theo biểu thuế lũy tiến từng phần"""
		if self.tax_exemption:
			return Decimal('0')

		taxable_income = self.calculate_taxable_income(gross_income)

		# Biểu thuế lũy tiến từng phần
		tax = Decimal('0')

		if taxable_income <= Decimal('5000000'):  # Đến 5 triệu: 5%
			tax = taxable_income * Decimal('0.05')
		elif taxable_income <= Decimal('10000000'):  # Trên 5 đến 10 triệu: 10%
			tax = Decimal('5000000') * Decimal('0.05') + (taxable_income - Decimal('5000000')) * Decimal('0.1')
		elif taxable_income <= Decimal('18000000'):  # Trên 10 đến 18 triệu: 15%
			tax = Decimal('5000000') * Decimal('0.05') + Decimal('5000000') * Decimal('0.1') + (
						taxable_income - Decimal('10000000')) * Decimal('0.15')
		elif taxable_income <= Decimal('32000000'):  # Trên 18 đến 32 triệu: 20%
			tax = Decimal('5000000') * Decimal('0.05') + Decimal('5000000') * Decimal('0.1') + Decimal(
				'8000000') * Decimal('0.15') + (taxable_income - Decimal('18000000')) * Decimal('0.2')
		elif taxable_income <= Decimal('52000000'):  # Trên 32 đến 52 triệu: 25%
			tax = Decimal('5000000') * Decimal('0.05') + Decimal('5000000') * Decimal('0.1') + Decimal(
				'8000000') * Decimal('0.15') + Decimal('14000000') * Decimal('0.2') + (
						      taxable_income - Decimal('32000000')) * Decimal('0.25')
		elif taxable_income <= Decimal('80000000'):  # Trên 52 đến 80 triệu: 30%
			tax = Decimal('5000000') * Decimal('0.05') + Decimal('5000000') * Decimal('0.1') + Decimal(
				'8000000') * Decimal('0.15') + Decimal('14000000') * Decimal('0.2') + Decimal('20000000') * Decimal(
				'0.25') + (taxable_income - Decimal('52000000')) * Decimal('0.3')
		else:  # Trên 80 triệu: 35%
			tax = Decimal('5000000') * Decimal('0.05') + Decimal('5000000') * Decimal('0.1') + Decimal(
				'8000000') * Decimal('0.15') + Decimal('14000000') * Decimal('0.2') + Decimal('20000000') * Decimal(
				'0.25') + Decimal('28000000') * Decimal('0.3') + (taxable_income - Decimal('80000000')) * Decimal(
				'0.35')

		return tax.quantize(Decimal('0'))


class Dependent(models.Model):
	RELATIONSHIP_CHOICES = [
		('child', 'Con'),
		('spouse', 'Vợ/Chồng'),
		('parent', 'Bố/Mẹ'),
		('sibling', 'Anh/Chị/Em'),
		('other', 'Khác'),
	]

	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='dependent_persons')
	full_name = models.CharField(max_length=100, verbose_name='Họ và tên')
	relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, verbose_name='Quan hệ')
	date_of_birth = models.DateField(verbose_name='Ngày sinh')
	id_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số CMND/CCCD')
	start_date = models.DateField(verbose_name='Ngày bắt đầu')
	end_date = models.DateField(blank=True, null=True, verbose_name='Ngày kết thúc')
	is_active = models.BooleanField(default=True, verbose_name='Đang áp dụng')

	class Meta:
		verbose_name = 'Người phụ thuộc'
		verbose_name_plural = 'Người phụ thuộc'
		ordering = ['-start_date']

	def __str__(self):
		return f"{self.full_name} - {self.get_relationship_display()}"


class Discipline(models.Model):
	DISCIPLINE_TYPE_CHOICES = [
		('warning', 'Cảnh cáo'),
		('fine', 'Phạt tiền'),
		('suspension', 'Đình chỉ công tác'),
		('other', 'Khác'),
	]

	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='disciplines')
	date = models.DateField(verbose_name='Ngày')
	discipline_type = models.CharField(max_length=20, choices=DISCIPLINE_TYPE_CHOICES, verbose_name='Loại kỷ luật')
	amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Số tiền')
	note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_disciplines')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'Kỷ luật'
		verbose_name_plural = 'Kỷ luật'
		ordering = ['-date']

	def __str__(self):
		return f"{self.employee.full_name} - {self.get_discipline_type_display()} - {self.date}"


class Reward(models.Model):
	REWARD_TYPE_CHOICES = [
		('bonus', 'Thưởng'),
		('commission', 'Hoa hồng'),
		('achievement', 'Thành tích'),
		('other', 'Khác'),
	]

	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='rewards')
	date = models.DateField(verbose_name='Ngày')
	reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, verbose_name='Loại khen thưởng')
	amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Số tiền')
	note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rewards')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'Khen thưởng'
		verbose_name_plural = 'Khen thưởng'
		ordering = ['-date']

	def __str__(self):
		return f"{self.employee.full_name} - {self.get_reward_type_display()} - {self.date}"