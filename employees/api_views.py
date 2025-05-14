# from django.http import JsonResponse
# from django.db.models import Q
# from .models import Employee
#
#
# def employee_search(request):
#     query = request.GET.get('q', '')
#     if len(query) < 2:
#         return JsonResponse([], safe=False)
#
#     employees = Employee.objects.filter(
#         Q(code__icontains=query) |
#         Q(first_name__icontains=query) |
#         Q(last_name__icontains=query) |
#         Q(full_name__icontains=query) |
#         Q(email__icontains=query)
#     ).filter(is_active=True)[:10]
#
#     results = []
#     for employee in employees:
#         results.append({
#             'id': employee.id,
#             'code': employee.code,
#             'full_name': employee.full_name,
#             'position': employee.position.name if employee.position else '',
#             'department': employee.department.name if employee.department else ''
#         })
#
#     return JsonResponse(results, safe=False)

from django.http import JsonResponse
from django.db.models import Q
from .models import Employee


def employee_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)

    employees = Employee.objects.filter(
        Q(code__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(full_name__icontains=query) |
        Q(email__icontains=query)
    ).filter(is_active=True)[:10]

    results = []
    for employee in employees:

        results.append({
            'id': employee.id,
            'code': employee.code,
            'full_name': employee.full_name,
            'position': employee.position.name if employee.position else '',

        })

    return JsonResponse(results, safe=False)