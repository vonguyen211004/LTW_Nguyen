from django import forms
from .models import Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['name', 'month', 'year', 'position' , 'attendance_summary', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'attendance_summary': forms.Select(attrs={'class': 'form-control'}),
        }


class PayrollDetailForm(forms.ModelForm):
    class Meta:
        model = PayrollDetail
        fields = [
            'basic_salary', 'standard_workdays', 'actual_workdays',
            'unpaid_leave',

        ]



class PayrollAllowanceForm(forms.ModelForm):
    class Meta:
        model = PayrollAllowance
        fields = ['name', 'amount', 'is_percentage']

class PayrollDeductionForm(forms.ModelForm):
    class Meta:
        model = PayrollDeduction
        fields = ['name', 'amount', 'is_percentage']