from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from decimal import Decimal
from .models import AttendanceSummary, DailyAttendance
from employees.models import Employee
import logging


def get_attendance_summary_data(attendance_summary_or_id):
	"""
	Lấy dữ liệu chấm công tổng hợp cho bảng chấm công
	Tham số có thể là đối tượng AttendanceSummary hoặc ID của nó
	"""
	# Thiết lập logging
	logger = logging.getLogger(__name__)

	# Kiểm tra xem tham số là đối tượng hay ID
	if isinstance(attendance_summary_or_id, int) or isinstance(attendance_summary_or_id, str):
		# Nếu là ID, lấy đối tượng AttendanceSummary
		try:
			attendance_summary = get_object_or_404(AttendanceSummary, id=attendance_summary_or_id)
			logger.info(f"Lấy dữ liệu chấm công tổng hợp cho ID: {attendance_summary_or_id}")
		except Exception as e:
			logger.error(f"Lỗi khi lấy đối tượng AttendanceSummary với ID {attendance_summary_or_id}: {str(e)}")
			return []
	else:
		# Nếu là đối tượng, sử dụng trực tiếp
		attendance_summary = attendance_summary_or_id
		logger.info(f"Lấy dữ liệu chấm công tổng hợp cho ID: {attendance_summary.id}")

	try:
		# Sử dụng đối tượng attendance_summary
		position = attendance_summary.position
		employees = Employee.objects.filter(position=position)
		logger.info(f"Đã tìm thấy {employees.count()} nhân viên cho vị trí {position.name}")

		# Lấy danh sách bảng chấm công chi tiết
		attendance_records = attendance_summary.attendance_records.all()
		logger.info(f"Đã tìm thấy {attendance_records.count()} bảng chấm công chi tiết")

		# Xác định khoảng thời gian của bảng chấm công tổng hợp
		if attendance_records:
			start_date = min(record.start_date for record in attendance_records)
			end_date = max(record.end_date for record in attendance_records)
			logger.info(f"Khoảng thời gian: {start_date} đến {end_date}")
		else:
			start_date = datetime.now().date()
			end_date = start_date
			logger.warning("Không có bảng chấm công chi tiết, sử dụng ngày hiện tại")

		# Tính số ngày làm việc (loại bỏ ngày Chủ nhật)
		delta = (end_date - start_date).days + 1
		working_days = 0
		current_date = start_date
		while current_date <= end_date:
			if current_date.weekday() != 6:  # 6 là Chủ nhật
				working_days += 1
			current_date += timedelta(days=1)
		logger.info(f"Số ngày làm việc: {working_days}")

		# Chuẩn bị dữ liệu cho từng nhân viên
		employee_data = []
		for employee in employees:
			logger.info(f"Đang xử lý nhân viên: {employee.full_name}")

			# Lấy tất cả bản ghi chấm công hàng ngày của nhân viên trong khoảng thời gian
			daily_attendances = DailyAttendance.objects.filter(
				attendance_record__in=attendance_records,
				employee=employee,
				date__range=[start_date, end_date]
			)
			logger.info(f"Đã tìm thấy {daily_attendances.count()} bản ghi chấm công hàng ngày")

			# Tính số công chuẩn (số ngày làm việc × work_days của ca làm việc)
			work_days_per_day = 1.0  # Giá trị mặc định
			if daily_attendances:
				# Lấy ca làm việc từ bản ghi đầu tiên (giả sử nhân viên chỉ có một ca)
				first_attendance = daily_attendances.first()
				if first_attendance and first_attendance.work_shift:
					work_days_per_day = first_attendance.work_shift.work_days
					logger.info(f"Số công mỗi ngày: {work_days_per_day}")
				else:
					logger.warning("Không tìm thấy ca làm việc, sử dụng giá trị mặc định")
			standard_work_days = working_days * work_days_per_day
			logger.info(f"Số công chuẩn: {standard_work_days}")

			# Tính công ngày thường, công ngày nghỉ, công nghỉ chế độ, đi muộn/về sớm
			normal_work_days = 0.0
			rest_work_days = 0.0
			regime_work_days = 0.0
			late_early_minutes = 0

			for attendance in daily_attendances:
				if not attendance.work_shift:
					logger.warning(f"Bản ghi chấm công ngày {attendance.date} không có ca làm việc")
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
			logger.info(f"Số ngày nghỉ không lương: {unpaid_leave}")

			# Tính số ngày công thực tế
			actual_workdays = standard_work_days - unpaid_leave
			logger.info(f"Số ngày công thực tế: {actual_workdays}")


			employee_data.append({
				'employee': employee,
				'standard_work_days': standard_work_days,
				'normal_work_days': normal_work_days,
				'rest_work_days': rest_work_days,
				'regime_work_days': regime_work_days,
				'late_early_minutes': late_early_minutes,
				'unpaid_leave': unpaid_leave,
				'actual_workdays': actual_workdays,

			})

		logger.info(f"Đã xử lý xong dữ liệu cho {len(employee_data)} nhân viên")
		return employee_data

	except Exception as e:
		logger.error(f"Lỗi khi lấy dữ liệu chấm công tổng hợp: {str(e)}")
		# Trả về danh sách rỗng nếu có lỗi
		return []
