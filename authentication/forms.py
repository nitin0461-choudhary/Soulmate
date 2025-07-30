from django import forms
class Login(forms.Form):
    email_address=forms.EmailField()
    password=forms.CharField()
    remember_me=forms.BooleanField()
class SignUp(forms.Form):
    name=forms.CharField()   
    email=forms.EmailField() 
    password1=forms.CharField()
    password2=forms.CharField()
    terms=forms.BooleanField()
class Forget_Password(forms.Form):
    name=forms.CharField()    
    email=forms.EmailField()
    