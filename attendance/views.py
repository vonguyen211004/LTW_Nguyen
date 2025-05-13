from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal
import datetime

from .models import AttendanceSummary, AttendanceRecord
from employees.models import Employee, Position
from payroll.models import Payroll, PayrollDetail
from .utils import get_attendance_summary_data


@login_required
def attendance_dashboard(request):
	# Lấy tháng và năm hiện tại
	today = timezone.now()
	current_month = today.month
	current_year = today.year

	# Lấy các bảng chấm công tổng hợp của tháng hiện tại
	summaries = AttendanceSummary.objects.filter(month=current_month, year=current_year)

	# Thống kê
	total_employees = Employee.objects.filter(is_active=True).count()
	total_positions = Position.objects.count()

	return render(request, 'attendance/attendance_dashboard.html', {
		'summaries': summaries,
		'current_month': current_month,
		'current_year': current_year,
		'total_employees': total_employees,
		'total_positions': total_positions
	})


@login_required
def attendance_summary(request):
	month_filter = request.GET.get('month', '')
	year_filter = request.GET.get('year', '')
	position_filter = request.GET.get('position', '')

	# Lấy tháng và năm hiện tại nếu không có filter
	today = timezone.now()
	if not month_filter:
		month_filter = today.month
	if not year_filter:
		year_filter = today.year

	summaries = AttendanceSummary.objects.all()

	# Lọc theo tháng và năm
	if month_filter and year_filter:
		summaries = summaries.filter(month=month_filter, year=year_filter)

	# Lọc theo vị trí
	if position_filter:
		summaries = summaries.filter(position_id=position_filter)

	positions = Position.objects.all()

	return render(request, 'attendance/attendance_summary.html', {
		'summaries': summaries,
		'positions': positions,
		'month_filter': int(month_filter) if month_filter else '',
		'year_filter': int(year_filter) if year_filter else '',
		'position_filter': position_filter,
		'current_month': today.month,
		'current_year': today.year
	})


@login_required
def attendance_summary_view(request, id):
	attendance_summary = get_object_or_404(AttendanceSummary, pk=id)

	# Lấy dữ liệu chấm công tổng hợp
	employee_data = get_attendance_summary_data(attendance_summary)

	return render(request, 'attendance/attendance_summary_view.html', {
		'attendance_summary': attendance_summary,
		'employee_data': employee_data
	})


@login_required
def transfer_to_payroll(request, summary_id):
	attendance_summary = get_object_or_404(AttendanceSummary, pk=summary_id)

	# Kiểm tra xem đã chuyển tính lương chưa
	if attendance_summary.transferred:
		messages.warning(request, "Bảng chấm công này đã được chuyển tính lương trước đó.")
		return redirect('attendance_summary_view', id=summary_id)

	# Lấy dữ liệu chấm công tổng hợp
	employee_data = get_attendance_summary_data(attendance_summary)

	if request.method == 'POST':
		if 'confirm' in request.POST:
			try:
				# Tạo bảng lương mới
				payroll = Payroll.objects.create(
					name=f"Bảng lương {attendance_summary.position.name} - {attendance_summary.month}/{attendance_summary.year}",
					month=attendance_summary.month,
					year=attendance_summary.year,
					position=attendance_summary.position,
					status='draft',
					created_by=request.user
				)

				# Tạo chi tiết lương cho từng nhân viên
				for data in employee_data:
					employee = data['employee']

					# Tính tổng tiền kỷ luật trong tháng
					discipline_amount = Decimal('0')
					disciplines = employee.disciplines.filter(
						date__month=attendance_summary.month,
						date__year=attendance_summary.year
					)
					for discipline in disciplines:
						discipline_amount += discipline.amount

					# Tính tổng tiền khen thưởng trong tháng
					reward_amount = Decimal('0')
					rewards = employee.rewards.filter(
						date__month=attendance_summary.month,
						date__year=attendance_summary.year
					)
					for reward in rewards:
						reward_amount += reward.amount

					# Tính lương theo ngày công
					gross_salary = employee.basic_salary * data['attendance_ratio']

					# Tính thuế TNCN
					taxable_income = employee.calculate_taxable_income(gross_salary + reward_amount)
					income_tax = employee.calculate_income_tax(gross_salary + reward_amount)

					# Tính lương thực lĩnh
					net_salary = gross_salary + reward_amount - income_tax - discipline_amount

					# Tạo chi tiết lương
					PayrollDetail.objects.create(
						payroll=payroll,
						employee=employee,
						basic_salary=employee.basic_salary,
						standard_workdays=data['standard_work_days'],
						actual_workdays=data['actual_workdays'],
						unpaid_leave=data['unpaid_leave'],
						attendance_ratio=data['attendance_ratio'],
						gross_salary=gross_salary,
						taxable_income=taxable_income,
						income_tax=income_tax,
						discipline_amount=discipline_amount,
						reward_amount=reward_amount,
						net_salary=net_salary
					)

				# Đánh dấu bảng chấm công đã chuyển tính lương
				attendance_summary.transferred = True
				attendance_summary.save()

				messages.success(request,
				                 f"Đã chuyển dữ liệu từ bảng chấm công sang bảng lương thành công. Bảng lương mới đã được tạo.")
				return redirect('payroll_detail', pk=payroll.id)

			except Exception as e:
				messages.error(request, f"Có lỗi xảy ra khi chuyển tính lương: {str(e)}")
				return redirect('attendance_summary_view', id=summary_id)
		else:
			return redirect('attendance_summary_view', id=summary_id)

	return render(request, 'attendance/transfer_to_payroll.html', {
		'attendance_summary': attendance_summary,
		'employee_data': employee_data
	})