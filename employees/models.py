from django.db import models
from django.contrib.auth.models import User


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
	full_name = models.CharField(max_length=100, verbose_name='Họ và tên', blank=True)
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

	# Thông tin khác
	photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True, verbose_name='Ảnh đại diện')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Nhân viên'
		verbose_name_plural = 'Nhân viên'
		ordering = ['last_name', 'first_name']

	def save(self, *args, **kwargs):
		# Tự động cập nhật full_name khi lưu
		self.full_name = f"{self.last_name} {self.first_name}"
		super().save(*args, **kwargs)