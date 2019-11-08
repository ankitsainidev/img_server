from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput,label='')
    userid = forms.CharField(label='')
    
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
class ClientForm(forms.Form):
    name = forms.CharField()
    textfile = forms.FileField(allow_empty_file=True)
    thumbs = forms.IntegerField()
    image = forms.ImageField()
    image1 = forms.ImageField(required=False)
    image2 = forms.ImageField(required = False)
class PassChangeForm(forms.Form):
    currentPassword = forms.CharField(widget=forms.PasswordInput,label='Current Password')
    NewPassword = forms.CharField(widget=forms.PasswordInput,label='New Password')
    ConfirmPassword = forms.CharField(widget=forms.PasswordInput,label='Confirm Password')
class ClientEditForm(forms.Form):
    name = forms.CharField(required=False)
    textfile = forms.FileField(allow_empty_file=True,required=False)
    thumbs = forms.IntegerField(required=False)
    image = forms.ImageField(required=False)
    image1 = forms.ImageField(required=False)
    image2 = forms.ImageField(required = False)