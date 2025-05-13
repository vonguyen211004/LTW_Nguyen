from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from decimal import Decimal

from .models import Employee, Position, Dependent, Discipline, Reward
from .forms import EmployeeForm, DependentForm, DisciplineForm, RewardForm


@login_required
def employee_list(request):
	search_query = request.GET.get('search', '')
	position_filter = request.GET.get('position', '')
	status_filter = request.GET.get('status', '')

	employees = Employee.objects.all()

	# Tìm kiếm
	if search_query:
		employees = employees.filter(
			Q(code__icontains=search_query) |
			Q(first_name__icontains=search_query) |
			Q(last_name__icontains=search_query) |
			Q(phone__icontains=search_query) |
			Q(email__icontains=search_query)
		)

	# Lọc theo vị trí
	if position_filter:
		employees = employees.filter(position_id=position_filter)

	# Lọc theo trạng thái
	if status_filter:
		is_active = status_filter == 'active'
		employees = employees.filter(is_active=is_active)

	positions = Position.objects.all()

	return render(request, 'employees/employee_list.html', {
		'employees': employees,
		'positions': positions,
		'search_query': search_query,
		'position_filter': position_filter,
		'status_filter': status_filter
	})


@login_required
def employee_detail(request, pk):
	employee = get_object_or_404(Employee, pk=pk)
	return render(request, 'employees/employee_detail.html', {
		'employee': employee
	})


@login_required
def employee_create(request):
	if request.method == 'POST':
		form = EmployeeForm(request.POST, request.FILES)
		if form.is_valid():
			employee = form.save()
			messages.success(request, f"Đã thêm nhân viên {employee.full_name}")
			return redirect('employee_detail', pk=employee.pk)
	else:
		form = EmployeeForm()

	positions = Position.objects.all()
	return render(request, 'employees/employee_form.html', {
		'form': form,
		'positions': positions
	})


@login_required
def employee_update(request, pk):
	employee = get_object_or_404(Employee, pk=pk)

	if request.method == 'POST':
		form = EmployeeForm(request.POST, request.FILES, instance=employee)
		if form.is_valid():
			employee = form.save()
			messages.success(request, f"Đã cập nhật thông tin nhân viên {employee.full_name}")
			return redirect('employee_detail', pk=employee.pk)
	else:
		form = EmployeeForm(instance=employee)

	positions = Position.objects.all()
	return render(request, 'employees/employee_form.html', {
		'form': form,
		'employee': employee,
		'positions': positions
	})


@login_required
def employee_delete(request, pk):
	employee = get_object_or_404(Employee, pk=pk)

	if request.method == 'POST':
		employee_name = employee.full_name
		employee.delete()
		messages.success(request, f"Đã xóa nhân viên {employee_name}")
		return redirect('employee_list')

	return render(request, 'employees/employee_confirm_delete.html', {
		'employee': employee
	})


# Quản lý người phụ thuộc
@login_required
def dependent_create(request, employee_id):
	employee = get_object_or_404(Employee, pk=employee_id)

	if request.method == 'POST':
		form = DependentForm(request.POST)
		if form.is_valid():
			dependent = form.save(commit=False)
			dependent.employee = employee
			dependent.save()
			messages.success(request, f"Đã thêm người phụ thuộc cho nhân viên {employee.full_name}")
			return redirect('employee_detail', pk=employee_id)
	else:
		form = DependentForm()

	return render(request, 'employees/dependent_form.html', {
		'form': form,
		'employee': employee,
		'title': 'Thêm người phụ thuộc'
	})


@login_required
def dependent_update(request, pk):
	dependent = get_object_or_404(Dependent, pk=pk)
	employee = dependent.employee

	if request.method == 'POST':
		form = DependentForm(request.POST, instance=dependent)
		if form.is_valid():
			form.save()
			messages.success(request, f"Đã cập nhật thông tin người phụ thuộc")
			return redirect('employee_detail', pk=employee.id)
	else:
		form = DependentForm(instance=dependent)

	return render(request, 'employees/dependent_form.html', {
		'form': form,
		'employee': employee,
		'dependent': dependent,
		'title': 'Cập nhật người phụ thuộc'
	})


@login_required
def dependent_delete(request, pk):
	dependent = get_object_or_404(Dependent, pk=pk)
	employee = dependent.employee

	if request.method == 'POST':
		dependent.delete()
		messages.success(request, f"Đã xóa người phụ thuộc")
		return redirect('employee_detail', pk=employee.id)

	return render(request, 'employees/dependent_confirm_delete.html', {
		'dependent': dependent,
		'employee': employee
	})


# Quản lý kỷ luật
@login_required
def discipline_create(request, employee_id):
	employee = get_object_or_404(Employee, pk=employee_id)

	if request.method == 'POST':
		form = DisciplineForm(request.POST)
		if form.is_valid():
			discipline = form.save(commit=False)
			discipline.employee = employee
			discipline.created_by = request.user
			discipline.save()
			messages.success(request, f"Đã thêm kỷ luật cho nhân viên {employee.full_name}")
			return redirect('employee_detail', pk=employee_id)
	else:
		form = DisciplineForm()

	return render(request, 'employees/discipline_form.html', {
		'form': form,
		'employee': employee,
		'title': 'Thêm kỷ luật'
	})


@login_required
def discipline_update(request, pk):
	discipline = get_object_or_404(Discipline, pk=pk)
	employee = discipline.employee

	if request.method == 'POST':
		form = DisciplineForm(request.POST, instance=discipline)
		if form.is_valid():
			form.save()
			messages.success(request, f"Đã cập nhật thông tin kỷ luật")
			return redirect('employee_detail', pk=employee.id)
	else:
		form = DisciplineForm(instance=discipline)

	return render(request, 'employees/discipline_form.html', {
		'form': form,
		'employee': employee,
		'discipline': discipline,
		'title': 'Cập nhật kỷ luật'
	})


@login_required
def discipline_delete(request, pk):
	discipline = get_object_or_404(Discipline, pk=pk)
	employee = discipline.employee

	if request.method == 'POST':
		discipline.delete()
		messages.success(request, f"Đã xóa kỷ luật")
		return redirect('employee_detail', pk=employee.id)

	return render(request, 'employees/discipline_confirm_delete.html', {
		'discipline': discipline,
		'employee': employee
	})


# Quản lý khen thưởng
@login_required
def reward_create(request, employee_id):
	employee = get_object_or_404(Employee, pk=employee_id)

	if request.method == 'POST':
		form = RewardForm(request.POST)
		if form.is_valid():
			reward = form.save(commit=False)
			reward.employee = employee
			reward.created_by = request.user
			reward.save()
			messages.success(request, f"Đã thêm khen thưởng cho nhân viên {employee.full_name}")
			return redirect('employee_detail', pk=employee_id)
	else:
		form = RewardForm()

	return render(request, 'employees/reward_form.html', {
		'form': form,
		'employee': employee,
		'title': 'Thêm khen thưởng'
	})


@login_required
def reward_update(request, pk):
	reward = get_object_or_404(Reward, pk=pk)
	employee = reward.employee

	if request.method == 'POST':
		form = RewardForm(request.POST, instance=reward)
		if form.is_valid():
			form.save()
			messages.success(request, f"Đã cập nhật thông tin khen thưởng")
			return redirect('employee_detail', pk=employee.id)
	else:
		form = RewardForm(instance=reward)

	return render(request, 'employees/reward_form.html', {
		'form': form,
		'employee': employee,
		'reward': reward,
		'title': 'Cập nhật khen thưởng'
	})


@login_required
def reward_delete(request, pk):
	reward = get_object_or_404(Reward, pk=pk)
	employee = reward.employee

	if request.method == 'POST':
		reward.delete()
		messages.success(request, f"Đã xóa khen thưởng")
		return redirect('employee_detail', pk=employee.id)

	return render(request, 'employees/reward_confirm_delete.html', {
		'reward': reward,
		'employee': employee
	})


@login_required
@require_POST
def calculate_tax_api(request, employee_id):
	"""API để tính thuế TNCN cho nhân viên"""
	try:
		employee = get_object_or_404(Employee, pk=employee_id)
		data = json.loads(request.body)
		gross_income = Decimal(str(data.get('gross_income', 0)))

		# Tính thu nhập tính thuế
		taxable_income = employee.calculate_taxable_income(gross_income)

		# Tính thuế TNCN
		income_tax = employee.calculate_income_tax(gross_income)

		# Tính lương thực lĩnh
		net_salary = gross_income - income_tax

		return JsonResponse({
			'gross_income': float(gross_income),
			'taxable_income': float(taxable_income),
			'income_tax': float(income_tax),
			'net_salary': float(net_salary)
		})
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=400)