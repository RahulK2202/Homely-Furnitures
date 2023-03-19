from django import forms
from order.models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'min_value', 'valid_from', 'valid_at', 'active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
