from django import forms
from .models import WorkShift, AttendanceRecord, DailyAttendance, AttendanceSummary
from employees.models import Position, Employee
from django.utils import timezone
from datetime import datetime, timedelta


class WorkShiftForm(forms.ModelForm):
    class Meta:
        model = WorkShift
        fields = ['name', 'code', 'start_time', 'check_in_start', 'check_in_end',
                 'end_time', 'check_out_start', 'check_out_end', 'has_break',
                 'work_hours', 'work_days', 'normal_day_coefficient',
                 'rest_day_coefficient', 'holiday_coefficient',
                 'deduct_if_no_check_in', 'deduct_if_no_check_out', 'apply_to_all', 'employees']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_in_start': forms.TimeInput(attrs={'type': 'time'}),
            'check_in_end': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_start': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_end': forms.TimeInput(attrs={'type': 'time'}),
            'employees': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Thêm class cho các trường
        for field_name, field in self.fields.items():
            if field_name not in ['employees']:  # Đã thiết lập ở trên
                field.widget.attrs['class'] = 'form-control'


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['name', 'start_date', 'end_date', 'positions', 'attendance_type', 'apply_to_all_shifts',
                  'work_shifts']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'work_shifts': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Chỉ hiển thị các vị trí đang hoạt động
        self.fields['positions'].queryset = Position.objects.filter(is_active=True)

        # Chỉ hiển thị các ca làm việc đang hoạt động
        self.fields['work_shifts'].queryset = WorkShift.objects.all()

        # Thêm class cho các trường
        for field_name, field in self.fields.items():
            if field_name not in ['work_shifts']:  # Đã thiết lập ở trên
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Ngày bắt đầu không thể sau ngày kết thúc")

        return cleaned_data


# Thay thế AttendanceSheetForm bằng một form thông thường vì không có model AttendanceSheet
class AttendanceSheetForm(forms.Form):
    name = forms.CharField(max_length=200, label="Tên bảng chấm công",
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    month = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)], label="Tháng",
                             widget=forms.Select(attrs={'class': 'form-select'}), null=True)
    year = forms.ChoiceField(choices=[(i, i) for i in range(2020, 2031)], label="Năm",
                            widget=forms.Select(attrs={'class': 'form-select'}), null=True)
    positions = forms.ModelMultipleChoiceField(
        queryset=Position.objects.filter(is_active=True),
        label="Vị trí áp dụng",
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    standard_workdays = forms.IntegerField(
        initial=24,
        label="Số công chuẩn",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    paid_leave = forms.IntegerField(
        initial=0,
        label="Nghỉ có phép",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    unpaid_leave = forms.IntegerField(
        initial=0,
        label="Nghỉ không phép",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    policy_leave = forms.IntegerField(
        initial=0,
        label="Nghỉ chế độ",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    attendance_type = forms.ChoiceField(
        choices=[('shift', 'Theo ca'), ('daily', 'Theo ngày')],
        label="Hình thức chấm công",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AttendanceSummaryForm(forms.ModelForm):
    class Meta:
        model = AttendanceSummary
        fields = ['name', 'position', 'attendance_records']
        widgets = {
            'attendance_records': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Chỉ hiển thị các vị trí đang hoạt động
        self.fields['position'].queryset = Position.objects.filter(is_active=True)

        # Chỉ hiển thị các bảng chấm công chi tiết
        self.fields['attendance_records'].queryset = AttendanceRecord.objects.all()

        # Thêm class cho các trường
        for field_name, field in self.fields.items():
            if field_name not in ['attendance_records']:  # Đã thiết lập ở trên
                field.widget.attrs['class'] = 'form-control'


class DailyAttendanceForm(forms.Form):
    attendance_status = forms.ChoiceField(
        choices=[
            ('not_absent', 'Không nghỉ'),
            ('permitted_absence', 'Nghỉ có phép'),
            ('unpermitted_absence', 'Nghỉ không phép'),
            ('regime_absence', 'Nghỉ chế độ'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    check_in_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    check_out_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    paid_work_days = forms.DecimalField(
        max_digits=3,
        decimal_places=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '1'})
    )
    actual_work_days = forms.DecimalField(
        max_digits=3,
        decimal_places=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '1'})
    )


class TransferAttendanceForm(forms.Form):
    attendance_summary = forms.ModelChoiceField(
        queryset=AttendanceSummary.objects.all(),
        label="Bảng chấm công tổng hợp",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lọc các bảng chấm công tổng hợp chưa được chuyển tính lương
        self.fields['attendance_summary'].queryset = AttendanceSummary.objects.filter(
            transferred=False
        ).order_by('-created_at')
