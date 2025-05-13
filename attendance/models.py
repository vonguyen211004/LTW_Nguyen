from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee, Position


class AttendanceSummary(models.Model):
	name = models.CharField(max_length=100, verbose_name='Tên bảng chấm công')
	month = models.PositiveIntegerField(verbose_name='Tháng', null=True)
	year = models.PositiveIntegerField(verbose_name='Năm', null = True)
	position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='attendance_summaries',
	                             verbose_name='Vị trí')
	transferred = models.BooleanField(default=False, verbose_name='Đã chuyển tính lương')
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
	                               related_name='created_attendance_summaries')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Bảng chấm công tổng hợp'
		verbose_name_plural = 'Bảng chấm công tổng hợp'
		ordering = ['-year', '-month']
		unique_together = ['month', 'year', 'position']

	def __str__(self):
		return f"Bảng chấm công {self.position.name} - {self.month}/{self.year}"


class AttendanceRecord(models.Model):
	attendance_summary = models.ForeignKey(AttendanceSummary, on_delete=models.CASCADE, related_name='attendance_records', null=True)
	employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='attendance_records', null=True)
	standard_work_days = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='Công chuẩn', null=True)
	normal_work_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Công ngày thường')
	rest_work_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Công ngày nghỉ')
	unpaid_leave = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='Nghỉ không lương')
	late_early_minutes = models.PositiveIntegerField(default=0, verbose_name='Đi muộn/về sớm (phút)')
	note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')

	class Meta:
		verbose_name = 'Bảng chấm công chi tiết'
		verbose_name_plural = 'Bảng chấm công chi tiết'
		ordering = ['employee__last_name', 'employee__first_name']
		unique_together = ['attendance_summary', 'employee']

	def __str__(self):
		return f"{self.employee.full_name} - {self.attendance_summary.name}"

	@property
	def actual_workdays(self):
		"""Tổng số công thực tế"""
		return self.normal_work_days + self.rest_work_days

	@property
	def attendance_ratio(self):
		"""Tỷ lệ hưởng lương"""
		if self.standard_work_days == 0:
			return 0
		return self.actual_workdays / self.standard_work_days