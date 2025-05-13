from django import forms
from .models import Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['name', 'month', 'year', 'position', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class PayrollDetailForm(forms.ModelForm):
    class Meta:
        model = PayrollDetail
        fields = [
            'basic_salary', 'standard_workdays', 'actual_workdays',
            'unpaid_leave', 'attendance_ratio', 'discipline_amount',
            'reward_amount', 'deduction_amount', 'note'
        ]
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class PayrollAllowanceForm(forms.ModelForm):
    class Meta:
        model = PayrollAllowance
        fields = ['name', 'amount', 'is_percentage']

class PayrollDeductionForm(forms.ModelForm):
    class Meta:
        model = PayrollDeduction
        fields = ['name', 'amount', 'is_percentage']