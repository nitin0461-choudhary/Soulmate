from django import forms

class Login(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)


class SignUp(forms.Form):
    name = forms.CharField(max_length=255)   
    email = forms.EmailField() 
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    terms = forms.BooleanField(required=True)


class Forget_Password(forms.Form):
    name = forms.CharField(max_length=255)    
    email = forms.EmailField()
