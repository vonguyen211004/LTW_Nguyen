from django import forms
from .models import Employee, Position, Dependent, Discipline, Reward

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'code', 'first_name', 'last_name', 'gender', 'date_of_birth', 'id_number',
            'phone', 'email', 'address',
            'position', 'join_date', 'is_active',
            'education_level', 'degree', 'major',
            'basic_salary', 'photo',
            'tax_code', 'tax_exemption', 'dependents'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DependentForm(forms.ModelForm):
    class Meta:
        model = Dependent
        fields = ['full_name', 'relationship', 'date_of_birth', 'id_number', 'start_date', 'end_date', 'is_active']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
        }

class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ['date', 'discipline_type', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['date', 'reward_type', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }