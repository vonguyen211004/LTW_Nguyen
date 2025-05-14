from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Employee, Position
from .forms import (EmployeeForm
                    )


# Employee views
@login_required
def employee_list(request):
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')

    # Sửa lại dòng này
    employees = Employee.objects.all()

    if search_query:
        employees = employees.filter(
            Q(code__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if position_filter:
        employees = employees.filter(position_id=position_filter)

    # Nếu model Position không có trường is_active, sửa lại dòng này
    positions = Position.objects.all()  # Bỏ filter(is_active=True)
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'positions': positions,
        'search_query': search_query,
        'position_filter': position_filter,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    context = {
        'employee': employee,
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            # Gộp họ tên
            employee.full_name = f"{employee.last_name} {employee.first_name}"
            employee.save()
            messages.success(request, f'Nhân viên {employee.full_name} đã được tạo thành công')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'title': 'Thêm nhân viên mới',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            # Cập nhật full_name trước khi lưu
            employee.full_name = f"{employee.last_name} {employee.first_name}"
            employee.save()
            messages.success(request, f'Thông tin nhân viên {employee.full_name} đã được cập nhật')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'Cập nhật thông tin nhân viên',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_deactivate(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = False
    employee.save()

    messages.success(request, f'Nhân viên {employee.full_name} đã được vô hiệu hóa.')
    return redirect('employee_list')


@login_required
def employee_activate(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = True
    employee.save()
    messages.success(request, f'Nhân viên {employee.full_name} đã được kích hoạt lại.')
    return redirect('employee_list')

# Personnel views
@login_required
def personnel_overview(request):
    total_employees = Employee.objects.filter(is_active=True).count()
    total_positions = Position.objects.filter(is_active=True).count()

    context = {
        'total_employees': total_employees,
        'total_positions': total_positions,
    }
    return render(request, 'personnel/overview.html', context)


@login_required
def personnel_profile(request):
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')

    employees = Employee.objects.all()

    if search_query:
        employees = employees.filter(
            Q(code__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if position_filter:
        employees = employees.filter(position_id=position_filter)

    positions = Position.objects.filter(is_active=True)

    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'positions': positions,
        'search_query': search_query,
        'position_filter': position_filter,
    }
    return render(request, 'personnel/profile_list.html', context)
