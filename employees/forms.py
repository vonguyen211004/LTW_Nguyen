from django import forms
from .models import Employee, Position
from django.utils.translation import gettext_lazy as _

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'code', 'first_name', 'last_name', 'gender', 'date_of_birth', 'id_number',
            'phone', 'email', 'address', 'position', 'join_date', 'is_active',
            'education_level', 'degree', 'major', 'basic_salary', 'photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '100000'}),
        }
        labels = {
            'code': _('Mã nhân viên'),
            'first_name': _('Tên'),
            'last_name': _('Họ'),
            'gender': _('Giới tính'),
            'date_of_birth': _('Ngày sinh'),
            'id_number': _('Số CMND/CCCD'),
            'phone': _('Số điện thoại'),
            'email': _('Email'),
            'address': _('Địa chỉ'),
            'position': _('Vị trí công việc'),
            'join_date': _('Ngày vào làm'),
            'is_active': _('Đang làm việc'),
            'education_level': _('Trình độ học vấn'),
            'degree': _('Bằng cấp'),
            'major': _('Chuyên ngành'),
            'basic_salary': _('Lương cơ bản (VNĐ)'),
            'photo': _('Ảnh đại diện'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm placeholder và các thuộc tính khác
        self.fields['code'].widget.attrs.update({'placeholder': 'Ví dụ: NV001'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Nhập tên'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Nhập họ'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Nhập số điện thoại'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Nhập email'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Nhập địa chỉ'})
        self.fields['id_number'].widget.attrs.update({'placeholder': 'Nhập số CMND/CCCD'})
        self.fields['degree'].widget.attrs.update({'placeholder': 'Ví dụ: Cử nhân Anh ngữ'})
        self.fields['major'].widget.attrs.update({'placeholder': 'Ví dụ: Ngôn ngữ Anh'})
        self.fields['basic_salary'].widget.attrs.update({'placeholder': 'Ví dụ: 10000000'})
