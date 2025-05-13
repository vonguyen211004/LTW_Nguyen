def get_attendance_summary_data(summary_id):
	# Lấy thông tin bảng chấm công
	from django.shortcuts import get_object_or_404
	from attendance.models import AttendanceSummary, DailyAttendance
	from employees.models import Employee
	from datetime import datetime, timedelta
	from decimal import Decimal

	attendance_summary = get_object_or_404(AttendanceSummary, id=summary_id)
	position = attendance_summary.position
	employees = Employee.objects.filter(position=position)

	# Lấy danh sách bảng chấm công chi tiết
	attendance_records = attendance_summary.attendance_records.all()

	# Xác định khoảng thời gian của bảng chấm công tổng hợp
	if attendance_records:
		start_date = min(record.start_date for record in attendance_records)
		end_date = max(record.end_date for record in attendance_records)
	else:
		start_date = datetime.now().date()
		end_date = start_date

	# Tính số ngày làm việc (loại bỏ ngày Chủ nhật)
	delta = (end_date - start_date).days + 1
	working_days = 0
	current_date = start_date
	while current_date <= end_date:
		if current_date.weekday() != 6:  # 6 là Chủ nhật
			working_days += 1
		current_date += timedelta(days=1)

	# Chuẩn bị dữ liệu cho từng nhân viên
	employee_data = []
	for employee in employees:
		# Lấy tất cả bản ghi chấm công hàng ngày của nhân viên trong khoảng thời gian
		daily_attendances = DailyAttendance.objects.filter(
			attendance_record__in=attendance_records,
			employee=employee,
			date__range=[start_date, end_date]
		)

		# Tính số công chuẩn (số ngày làm việc × work_days của ca làm việc)
		work_days_per_day = 1.0  # Giá trị mặc định
		if daily_attendances:
			# Lấy ca làm việc từ bản ghi đầu tiên (giả sử nhân viên chỉ có một ca)
			work_shift = daily_attendances.first().work_shift
			if work_shift:
				work_days_per_day = work_shift.work_days
		standard_work_days = working_days * work_days_per_day

		# Tính công ngày thường, công ngày nghỉ, công nghỉ chế độ, đi muộn/về sớm
		normal_work_days = 0.0
		rest_work_days = 0.0
		regime_work_days = 0.0
		late_early_minutes = 0

		for attendance in daily_attendances:
			if not attendance.work_shift:
				continue

			# Xác định hệ số dựa trên ngày
			normal_coefficient = attendance.work_shift.normal_day_coefficient
			rest_coefficient = attendance.work_shift.rest_day_coefficient

			# Kiểm tra ngày nghỉ (giả sử thứ 7, chủ nhật là ngày nghỉ)
			day_of_week = attendance.date.weekday()  # 0: Thứ 2, ..., 5: Thứ 7, 6: Chủ nhật
			is_rest_day = day_of_week >= 5  # Thứ 7 hoặc Chủ nhật

			# Tính công ngày thường và công ngày nghỉ
			if attendance.attendance_status != "unpermitted_absence":
				if is_rest_day:
					rest_work_days += attendance.actual_work_days * rest_coefficient
				else:
					normal_work_days += attendance.actual_work_days * normal_coefficient

			# Tính công nghỉ chế độ
			if attendance.attendance_status == "regime_absence":
				regime_work_days += attendance.actual_work_days

			# Tính số phút đi muộn/về sớm
			if attendance.check_in_time and attendance.work_shift.check_in_end:
				check_in_time_total = attendance.check_in_time.hour * 3600 + attendance.check_in_time.minute * 60 + attendance.check_in_time.second
				check_in_end_total = attendance.work_shift.check_in_end.hour * 3600 + attendance.work_shift.check_in_end.minute * 60 + attendance.work_shift.check_in_end.second
				if check_in_time_total > check_in_end_total:
					late_minutes = (check_in_time_total - check_in_end_total) // 60
					late_early_minutes += late_minutes

			if attendance.check_out_time and attendance.work_shift.check_out_start:
				check_out_time_total = attendance.check_out_time.hour * 3600 + attendance.check_out_time.minute * 60 + attendance.check_out_time.second
				check_out_start_total = attendance.work_shift.check_out_start.hour * 3600 + attendance.work_shift.check_out_start.minute * 60 + attendance.work_shift.check_out_start.second
				if check_out_time_total < check_out_start_total:
					early_minutes = (check_out_start_total - check_out_time_total) // 60
					late_early_minutes += early_minutes

		# Tính số ngày nghỉ không lương (unpaid_leave)
		unpaid_leave = 0
		for attendance in daily_attendances:
			if attendance.attendance_status == "unpermitted_absence":
				unpaid_leave += 1

		# Tính số ngày công thực tế
		actual_workdays = standard_work_days - unpaid_leave

		# Tính tỷ lệ chuyên cần
		attendance_ratio = actual_workdays / standard_work_days if standard_work_days else 0

		employee_data.append({
			'employee': employee,
			'standard_work_days': standard_work_days,
			'normal_work_days': normal_work_days,
			'rest_work_days': rest_work_days,
			'regime_work_days': regime_work_days,
			'late_early_minutes': late_early_minutes,
			'unpaid_leave': unpaid_leave,
			'actual_workdays': actual_workdays,
			'attendance_ratio': round(attendance_ratio, 2),
		})

	return employee_data