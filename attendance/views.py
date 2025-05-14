from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import WorkShift, AttendanceRecord, DailyAttendance, AttendanceSummary
from employees.models import Employee, Position
from datetime import datetime, timedelta
from .utils import get_attendance_summary_data
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.shortcuts import redirect
from django.contrib import messages
from .models import AttendanceRecord
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal

from .models import AttendanceSummary, EmployeeAttendance
from payroll.models import Payroll, PayrollDetail
from .models import AttendanceSummary, AttendanceRecord


def dashboard(request):
    return redirect('work_shift_list')

def work_shift_list(request):
    work_shifts = WorkShift.objects.all()
    return render(request, 'attendance/work_shift_list.html', {'work_shifts': work_shifts})

def work_shift_form(request, id=None):
    if id:
        work_shift = get_object_or_404(WorkShift, id=id)
    else:
        work_shift = None

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        start_time = request.POST.get('start_time')
        check_in_start = request.POST.get('check_in_start')
        check_in_end = request.POST.get('check_in_end')
        end_time = request.POST.get('end_time')
        check_out_start = request.POST.get('check_out_start')
        check_out_end = request.POST.get('check_out_end')
        has_break = request.POST.get('has_break') == 'on'
        work_hours = float(request.POST.get('work_hours', 0))
        work_days = float(request.POST.get('work_days', 1))
        normal_day_coefficient = float(request.POST.get('normal_day_coefficient', 1))
        rest_day_coefficient = float(request.POST.get('rest_day_coefficient', 2))
        holiday_coefficient = float(request.POST.get('holiday_coefficient', 3))
        deduct_if_no_check_in = request.POST.get('deduct_if_no_check_in') == 'on'
        deduct_if_no_check_out = request.POST.get('deduct_if_no_check_out') == 'on'
        apply_to_all = request.POST.get('apply_to_all') == 'yes'
        employee_ids = request.POST.getlist('employees')

        if work_shift:  # Sửa ca làm việc
            work_shift.name = name
            work_shift.code = code
            work_shift.start_time = start_time
            work_shift.check_in_start = check_in_start
            work_shift.check_in_end = check_in_end
            work_shift.end_time = end_time
            work_shift.check_out_start = check_out_start
            work_shift.check_out_end = check_out_end
            work_shift.has_break = has_break
            work_shift.work_hours = work_hours
            work_shift.work_days = work_days
            work_shift.normal_day_coefficient = normal_day_coefficient
            work_shift.rest_day_coefficient = rest_day_coefficient
            work_shift.holiday_coefficient = holiday_coefficient
            work_shift.deduct_if_no_check_in = deduct_if_no_check_in
            work_shift.deduct_if_no_check_out = deduct_if_no_check_out
            work_shift.apply_to_all = apply_to_all
            work_shift.save()
            if Employee:
                work_shift.employees.set(employee_ids)
            messages.success(request, "Cập nhật ca làm việc thành công!")
        else:  # Thêm ca làm việc mới
            work_shift = WorkShift.objects.create(
                name=name,
                code=code,
                start_time=start_time,
                check_in_start=check_in_start,
                check_in_end=check_in_end,
                end_time=end_time,
                check_out_start=check_out_start,
                check_out_end=check_out_end,
                has_break=has_break,
                work_hours=work_hours,
                work_days=work_days,
                normal_day_coefficient=normal_day_coefficient,
                rest_day_coefficient=rest_day_coefficient,
                holiday_coefficient=holiday_coefficient,
                deduct_if_no_check_in=deduct_if_no_check_in,
                deduct_if_no_check_out=deduct_if_no_check_out,
                apply_to_all=apply_to_all
            )
            if Employee and employee_ids:
                work_shift.employees.set(employee_ids)
            messages.success(request, "Thêm ca làm việc thành công!")

        return redirect('work_shift_list')

    employees = Employee.objects.all() if Employee else []

    return render(request, 'attendance/work_shift_form.html', {
        'work_shift': work_shift,
        'employees': employees
    })

def work_shift_detail(request, id):
    work_shift = get_object_or_404(WorkShift, id=id)
    return render(request, 'attendance/work_shift_detail.html', {'work_shift': work_shift})

def work_shift_delete(request, id):
    work_shift = get_object_or_404(WorkShift, id=id)
    work_shift.delete()
    messages.success(request, f"Đã xóa ca làm việc {work_shift.name} thành công!")
    return redirect('work_shift_list')

def attendance_detail_list(request):
    attendance_records = AttendanceRecord.objects.all()
    work_shifts = WorkShift.objects.all()  # Thêm danh sách ca làm việc
    return render(request, 'attendance/attendance_detail_list.html', {
        'attendance_records': attendance_records,
        'work_shifts': work_shifts
    })


def attendance_detail_save(request):
    if request.method == 'POST':
        # Get necessary data from POST request
        attendance_record_id = request.POST.get('attendance_record_id')
        employee_id = request.POST.get('employee_id')
        check_in_time = request.POST.get('check_in_time')
        check_out_time = request.POST.get('check_out_time')

        # Handle saving or updating the attendance record here
        attendance_record = AttendanceRecord.objects.get(id=attendance_record_id)
        # Update attendance record fields as needed
        # Example: attendance_record.check_in_time = check_in_time
        attendance_record.save()

        messages.success(request, "Attendance record saved successfully!")
        return redirect('attendance_detail_list')  # Redirect to the attendance detail list or another page

    return redirect('attendance_detail_list')  # Default redirect if method is not POST

def attendance_detail_form(request, id=None):
    if id:
        attendance_record = get_object_or_404(AttendanceRecord, id=id)
    else:
        attendance_record = None

    if request.method == 'POST':
        name = request.POST.get('name')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        attendance_type = request.POST.get('attendance_type')
        position_id = request.POST.get('positions')
        apply_to_all_shifts = request.POST.get('apply_to_all_shifts') == 'on'
        work_shift_ids = request.POST.getlist('work_shifts')

        # Chuyển đổi chuỗi ngày thành đối tượng datetime.date
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        position = get_object_or_404(Position, id=position_id)

        if attendance_record:  # Sửa bảng chấm công chi tiết
            attendance_record.name = name
            attendance_record.start_date = start_date
            attendance_record.end_date = end_date
            attendance_record.attendance_type = attendance_type
            attendance_record.positions = position
            attendance_record.apply_to_all_shifts = apply_to_all_shifts
            attendance_record.save()
            if not apply_to_all_shifts:
                attendance_record.work_shifts.set(work_shift_ids)
            else:
                attendance_record.work_shifts.clear()
            messages.success(request, "Cập nhật bảng chấm công chi tiết thành công!")
        else:  # Thêm mới bảng chấm công chi tiết
            attendance_record = AttendanceRecord.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                attendance_type=attendance_type,
                positions=position,
                apply_to_all_shifts=apply_to_all_shifts
            )
            if not apply_to_all_shifts:
                attendance_record.work_shifts.set(work_shift_ids)
            messages.success(request, "Thêm bảng chấm công chi tiết thành công!")

        return redirect('attendance_detail_list')

    positions = Position.objects.all()
    work_shifts = WorkShift.objects.all()
    return render(request, 'attendance/attendance_detail_form.html', {
        'attendance_record': attendance_record,
        'positions': positions,
        'work_shifts': work_shifts
    })



def attendance_detail_delete(request, id):
    attendance_record = get_object_or_404(AttendanceRecord, id=id)
    attendance_record.delete()
    messages.success(request, "Đã xóa bảng chấm công chi tiết thành công!")
    return redirect('attendance_detail_list')

def attendance_detail_view(request, id):
    attendance_record = get_object_or_404(AttendanceRecord, id=id)
    position = attendance_record.positions
    employees = Employee.objects.filter(position=position)

    # Tạo danh sách các ngày trong khoảng thời gian
    start_date = attendance_record.start_date
    end_date = attendance_record.end_date
    delta = end_date - start_date
    date_list = [(start_date + timedelta(days=i)) for i in range(delta.days + 1)]

    # Lấy dữ liệu chấm công cho từng nhân viên
    daily_attendances = DailyAttendance.objects.filter(attendance_record=attendance_record)
    attendance_data = {}
    for employee in employees:
        employee_attendance = {}
        for date in date_list:
            attendance = daily_attendances.filter(employee=employee, date=date).first()
            if attendance and attendance.check_in_time and attendance.work_shift:
                # So sánh thời gian để xác định đi đúng giờ/sớm hay muộn
                check_in_time = attendance.check_in_time
                check_in_end = attendance.work_shift.check_in_end

                # So sánh thời gian một cách chính xác
                check_in_time_total = check_in_time.hour * 3600 + check_in_time.minute * 60 + check_in_time.second
                check_in_end_total = check_in_end.hour * 3600 + check_in_end.minute * 60 + check_in_end.second

                # So sánh thời gian để xác định đủ công hay thiếu công
                is_enough_work = False
                if attendance.check_out_time:
                    check_out_time = attendance.check_out_time
                    check_out_start = attendance.work_shift.check_out_start

                    check_out_time_total = check_out_time.hour * 3600 + check_out_time.minute * 60 + check_out_time.second
                    check_out_start_total = check_out_start.hour * 3600 + check_out_start.minute * 60 + check_out_start.second

                    is_enough_work = check_out_time_total >= check_out_start_total

                print(f"Employee: {employee}, Date: {date}, check_in_time: {check_in_time}, check_in_end: {check_in_end}, is_on_time: {check_in_time_total <= check_in_end_total}, check_out_time: {attendance.check_out_time}, check_out_start: {attendance.work_shift.check_out_start}, is_enough_work: {is_enough_work}")

                employee_attendance[date] = {
                    'attendance': attendance,
                    'is_on_time': check_in_time_total <= check_in_end_total,
                    'is_enough_work': is_enough_work
                }
            else:
                employee_attendance[date] = {
                    'attendance': attendance,
                    'is_on_time': False,
                    'is_enough_work': False
                }
        attendance_data[employee.id] = employee_attendance

    return render(request, 'attendance/attendance_detail_view.html', {
        'attendance_record': attendance_record,
        'employees': employees,
        'date_list': date_list,
        'attendance_data': attendance_data,
    })

def update_daily_attendance(request, record_id, employee_id, date_str):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON từ request.body
            data = json.loads(request.body)
            print('Dữ liệu nhận được từ client:', data)  # Debug dữ liệu nhận được

            attendance_record = get_object_or_404(AttendanceRecord, id=record_id)
            employee = get_object_or_404(Employee, id=employee_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Lấy hoặc tạo bản ghi chấm công hàng ngày
            daily_attendance, created = DailyAttendance.objects.get_or_create(
                attendance_record=attendance_record,
                employee=employee,
                date=date,
                defaults={'attendance_status': 'not_absent'}  # Mặc định là "Không nghỉ" nếu chưa chấm
            )

            # Lấy dữ liệu từ payload
            paid_work_days = float(data.get('paid_work_days', 1))
            actual_work_days = float(data.get('actual_work_days', 1))
            check_in_time_str = data.get('check_in_time') or None
            check_out_time_str = data.get('check_out_time') or None
            attendance_status = data.get('attendance_status')

            # Kiểm tra attendance_status
            valid_statuses = [choice[0] for choice in DailyAttendance.ATTENDANCE_STATUS_CHOICES]
            if not attendance_status or attendance_status not in valid_statuses:
                return JsonResponse({'status': 'error', 'message': f'Trạng thái nghỉ không hợp lệ! Nhận được: "{attendance_status}", giá trị hợp lệ: {valid_statuses}'})

            # Chuyển đổi thời gian từ chuỗi (HH:MM)
            check_in_time = None
            check_out_time = None
            if check_in_time_str and check_in_time_str != 'null':
                try:
                    check_in_time = datetime.strptime(check_in_time_str, '%H:%M').time()
                except ValueError as e:
                    return JsonResponse({'status': 'error', 'message': f'Định dạng giờ vào không hợp lệ (HH:MM): {check_in_time_str}, lỗi: {str(e)}'})
            if check_out_time_str and check_out_time_str != 'null':
                try:
                    check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()
                except ValueError as e:
                    return JsonResponse({'status': 'error', 'message': f'Định dạng giờ ra không hợp lệ (HH:MM): {check_out_time_str}, lỗi: {str(e)}'})

            # Gán work_shift từ AttendanceRecord
            # Giả sử chỉ có một ca làm việc được chọn trong AttendanceRecord
            work_shift = None
            if attendance_record.apply_to_all_shifts:
                # Nếu áp dụng tất cả ca, lấy ca phù hợp với employee (cần logic cụ thể hơn)
                work_shift = WorkShift.objects.filter(employees=employee).first()
            else:
                # Lấy ca đầu tiên từ danh sách work_shifts của AttendanceRecord
                work_shift = attendance_record.work_shifts.first()

            if not work_shift:
                return JsonResponse({'status': 'error', 'message': 'Không tìm thấy ca làm việc phù hợp!'})

            # Cập nhật bản ghi
            daily_attendance.paid_work_days = paid_work_days
            daily_attendance.actual_work_days = actual_work_days
            daily_attendance.check_in_time = check_in_time
            daily_attendance.check_out_time = check_out_time
            daily_attendance.attendance_status = attendance_status
            daily_attendance.work_shift = work_shift  # Gán work_shift
            daily_attendance.save()

            return JsonResponse({'status': 'success', 'message': 'Chấm công thành công!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Lỗi khi lưu dữ liệu: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ!'})

def get_daily_attendance(request, record_id, employee_id, date_str):
    try:
        attendance_record = get_object_or_404(AttendanceRecord, id=record_id)
        employee = get_object_or_404(Employee, id=employee_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        daily_attendance = DailyAttendance.objects.filter(
            attendance_record=attendance_record,
            employee=employee,
            date=date
        ).first()

        if daily_attendance:
            data = {
                'paid_work_days': daily_attendance.paid_work_days,
                'actual_work_days': daily_attendance.actual_work_days,
                'check_in_time': daily_attendance.check_in_time.strftime('%H:%M') if daily_attendance.check_in_time else '',
                'check_out_time': daily_attendance.check_out_time.strftime('%H:%M') if daily_attendance.check_out_time else '',
                'attendance_status': daily_attendance.attendance_status,
            }
        else:
            data = {
                'paid_work_days': 1,
                'actual_work_days': 1,
                'check_in_time': '',
                'check_out_time': '',
                'attendance_status': 'not_absent',
            }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Lỗi khi lấy dữ liệu: {str(e)}'})

def attendance_summary(request):
    attendance_summaries = AttendanceSummary.objects.all()
    positions = Position.objects.all()  # Thêm danh sách vị trí
    attendance_records = AttendanceRecord.objects.all()  # Thêm danh sách bảng chấm công chi tiết
    return render(request, 'attendance/attendance_summary.html', {
        'attendance_summaries': attendance_summaries,
        'positions': positions,
        'attendance_records': attendance_records
    })

def attendance_summary_form(request, id=None):
    if id:
        attendance_summary = get_object_or_404(AttendanceSummary, id=id)
    else:
        attendance_summary = None

    if request.method == 'POST':
        name = request.POST.get('name')
        position_id = request.POST.get('position')
        attendance_record_ids = request.POST.getlist('attendance_records')

        position = get_object_or_404(Position, id=position_id)

        if attendance_summary:  # Sửa bảng chấm công tổng hợp
            attendance_summary.name = name
            attendance_summary.position = position
            attendance_summary.save()
            attendance_summary.attendance_records.set(attendance_record_ids)
            messages.success(request, "Cập nhật bảng chấm công tổng hợp thành công!")
        else:  # Thêm mới bảng chấm công tổng hợp
            attendance_summary = AttendanceSummary.objects.create(
                name=name,
                position=position
            )
            attendance_summary.attendance_records.set(attendance_record_ids)
            messages.success(request, "Thêm bảng chấm công tổng hợp thành công!")

        return redirect('attendance_summary')

    positions = Position.objects.all()
    attendance_records = AttendanceRecord.objects.all()
    return render(request, 'attendance/attendance_summary_form.html', {
        'attendance_summary': attendance_summary,
        'positions': positions,
        'attendance_records': attendance_records
    })

def attendance_summary_edit(request, id):
    summary = get_object_or_404(AttendanceSummary, id=id)
    # Logic để chỉnh sửa tại đây (form xử lý, POST/GET, ...)
    return render(request, 'attendance/attendance_summary_edit.html', {'summary': summary})

def attendance_summary_list(request):
    # Your view logic here
    return render(request, 'attendance/attendance_summary_list.html')
@login_required
def attendance_list(request):
    """Danh sách bảng chấm công tổng hợp"""
    # Lấy danh sách bảng chấm công tổng hợp
    attendance_summaries = AttendanceSummary.objects.all().order_by('-created_at')

    # Phân trang
    paginator = Paginator(attendance_summaries, 10)  # 10 bảng chấm công mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'attendance/attendance_list.html', context)
@login_required
def attendance_summary_view(request, id):
    """Xem chi tiết bảng chấm công tổng hợp"""
    attendance_summary = get_object_or_404(AttendanceSummary, id=id)

    # Lấy dữ liệu chấm công tổng hợp
    from .utils import get_attendance_summary_data
    employee_data = get_attendance_summary_data(attendance_summary)  # Truyền đối tượng thay vì ID

    context = {
        'attendance_summary': attendance_summary,
        'employee_data': employee_data,
    }

    return render(request, 'attendance/attendance_summary_view.html', context)


def attendance_summary_delete(request, id):
    attendance_summary = get_object_or_404(AttendanceSummary, id=id)
    attendance_summary.delete()
    messages.success(request, "Đã xóa bảng chấm công tổng hợp thành công!")
    return redirect('attendance_summary')


@login_required
def transfer_to_payroll(request, summary_id):
    """Chuyển dữ liệu từ bảng chấm công tổng hợp sang tính lương"""
    attendance_summary = get_object_or_404(AttendanceSummary, pk=summary_id)

    # Kiểm tra xem bảng chấm công đã được chuyển sang tính lương chưa
    if attendance_summary.transferred:
        messages.warning(request, 'Bảng chấm công này đã được chuyển sang tính lương trước đó')
        return redirect('attendance_summary_view', id=summary_id)

    # Lấy dữ liệu nhân viên từ hàm helper để hiển thị trong trang xác nhận
    employee_data = get_attendance_summary_data(summary_id)

    if request.method == 'POST':
        # Nếu người dùng đã xác nhận, thực hiện chuyển dữ liệu
        if 'confirm' in request.POST:
            try:
                # Xác định month và year từ attendance_summary hoặc sử dụng thời gian hiện tại
                month = getattr(attendance_summary, 'month', datetime.now().month)
                year = getattr(attendance_summary, 'year', datetime.now().year)

                # Tạo bảng lương mới
                payroll_name = f"Bảng lương tháng {month}/{year} - {attendance_summary.position.name}"
                payroll = Payroll.objects.create(
                    user=request.user , # ✅ thêm dòng này
                    name=payroll_name,
                    month=month,
                    year=year,
                    position=attendance_summary.position,
                    status='draft',
                    created_by=request.user
                )

                # Tính lương cho từng nhân viên
                for employee_info in employee_data:
                    employee = employee_info['employee']

                    # Lấy lương cơ bản từ thông tin nhân viên
                    basic_salary = getattr(employee, 'basic_salary', 0) or 0

                    # Lấy thông tin chấm công từ employee_data
                    standard_work_days = employee_info.get('standard_work_days', 0)
                    actual_workdays = employee_info.get('actual_workdays', 0)
                    unpaid_leave = employee_info.get('unpaid_leave', 0)

                    # Xử lý attendance_ratio một cách an toàn
                    attendance_ratio_raw = employee_info.get('attendance_ratio', 0)

                    # Đảm bảo attendance_ratio là một số hợp lệ
                    try:
                        attendance_ratio = float(attendance_ratio_raw)
                        # Đảm bảo tỷ lệ nằm trong khoảng hợp lệ (0-1)
                        attendance_ratio = max(0, min(1, attendance_ratio))
                    except (TypeError, ValueError):
                        attendance_ratio = 0

                    # Tính lương theo ngày công
                    try:
                        gross_salary = int(basic_salary * Decimal(str(attendance_ratio)))
                    except Exception:
                        gross_salary = 0

                    # Tính các khoản khấu trừ (giả định 10% tổng thu nhập)
                    deductions_amount = int(gross_salary * Decimal('0.1'))

                    # Tính lương thực lĩnh
                    net_salary = gross_salary - deductions_amount

                    PayrollDetail.objects.create(
                        payroll=payroll,
                        employee=employee,
                        basic_salary=basic_salary,
                        attendance_ratio=attendance_ratio,
                        standard_workdays=standard_work_days,
                        actual_workdays=actual_workdays,
                        unpaid_leave=unpaid_leave,
                        gross_salary=gross_salary,
                        deduction_amount=deductions_amount,
                        net_salary=net_salary

                    )

                # Đánh dấu bảng chấm công đã được chuyển tính lương
                attendance_summary.transferred = True
                attendance_summary.save()

                messages.success(request,
                                 f'Đã chuyển dữ liệu từ bảng chấm công "{attendance_summary.name}" sang bảng lương thành công')

                return render(request, 'attendance/transfer_to_payroll.html', context)
            except Exception as e:
                messages.error(request, f'Lỗi khi chuyển dữ liệu: {str(e)}')
                return redirect('attendance_summary_view', id=summary_id)
        else:
            # Người dùng đã hủy thao tác
            messages.info(request, 'Đã hủy thao tác chuyển tính lương')
            return redirect('attendance_summary_view', id=summary_id)

    # Hiển thị trang xác nhận
    context = {
        'attendance_summary': attendance_summary,
        'employee_data': employee_data,
    }

    return render(request, 'attendance/transfer_to_payroll.html', context)





