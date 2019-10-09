from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from blog import models


class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        min_length=4,
        error_messages={
            'required': '用户名不能为空',
            'min_length': '用户名不能少于四位',
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'
            }
        )
    )

    password = forms.CharField(
        label='密码',
        min_length=6,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码不能少于六位',
        },
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control", 'placeholder': '请输入密码'}
        )
    )

    re_password = forms.CharField(
        label='确认密码',
        min_length=6,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码不能少于六位',
        },
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control", 'placeholder': '请输入密码'}
        )
    )

    phone = forms.CharField(
        label='电话',
        error_messages={
            'required': '手机号不能为空',
        },
        validators=[RegexValidator(r'1[3-9]\d{9}', '电话号码格式错误')],

        widget=forms.widgets.TextInput(
            attrs={'class': 'form-control',  'placeholder': '请输入电话'}
        ),
    )

    email = forms.CharField(
        label='邮箱',
        error_messages={
            "required": "邮箱不能为空",
        },
        validators=[RegexValidator(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', "邮箱格式不正确")],
        widget=forms.widgets.EmailInput(
            attrs={"class": "form-control",  'placeholder': '请输入邮箱'}
        )
    )

    def clean_username(self):  # 局部钩子函数
        username = self.cleaned_data.get('username')
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            raise ValidationError('该用户名已经存在')
        else:
            return username

    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password == re_password:
            return self.cleaned_data
        else:
            self.add_error('re_password', '两次密码不一致')
            raise ValidationError('两次密码不一致')