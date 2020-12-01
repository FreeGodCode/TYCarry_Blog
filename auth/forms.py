# from django.forms import forms
from django import forms
from django.forms import widgets


class RequireEmailForm(forms.Form):
    """邮箱验证表单模型类"""
    email = forms.EmailField(verbose='电子邮箱', required=True)
    authid = forms.IntegerField(widget=forms.HiddenInput, required=True)

    def __init__(self, *args, **kwargs):
        super(RequireEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = widgets.EmailInput(attrs={'placeholder': 'email', 'class': 'form-control'})
