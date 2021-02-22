# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: forms.py
# @Time:  2021/2/20 下午7:02
# @Description:
from django.contrib.auth import forms
from django.forms import widgets


class RequireEmailForm(forms.Form):
    """邮件表单验证forms"""
    email = forms.EmailField(label='电子邮箱', required=True)
    oauthid = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(RequireEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = widgets.EmailInput(attrs={'placeholder': 'email', 'class': 'form-control'})
