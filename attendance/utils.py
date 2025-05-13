from decimal import Decimal


def get_attendance_summary_data(attendance_summary):
	"""
	Tính toán dữ liệu chấm công tổng hợp cho một bảng chấm công
	"""
	employee_data = []

	for record in attendance_summary.attendance_records.all():
		# Tính số công thực tế
		actual_workdays = record.normal_work_days + record.rest_work_days

		# Tính tỷ lệ hưởng lương
		attendance_ratio = Decimal('0')
		if record.standard_work_days > 0:
			attendance_ratio = actual_workdays / record.standard_work_days

		employee_data.append({
			'employee': record.employee,
			'standard_work_days': record.standard_work_days,
			'normal_work_days': record.normal_work_days,
			'rest_work_days': record.rest_work_days,
			'unpaid_leave': record.unpaid_leave,
			'late_early_minutes': record.late_early_minutes,
			'actual_workdays': actual_workdays,
			'attendance_ratio': attendance_ratio
		})

	return employee_data