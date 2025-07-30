from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.utils import timezone

from authentication.forms import Login,SignUp,Forget_Password
from authentication.models import Login_model
# from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password,check_password
def home(req):
      return  render(req,'authentication/home.html')

def Login_views(req):
        if req.method=='POST':
            form=Login(req.POST)
            if form.is_valid():
                inp_name=form.cleaned_data['name']
                inp_email=form.cleaned_data['email']
                inp_password=form.cleaned_data['password']
                remember_me=form.cleaned_data['remember_me']
                matched_user=Login_model.objects.filter(name=inp_name,email=inp_email).first()
                if matched_user and check_password(inp_password,matched_user.password):
                        req.session['User_id']=matched_user.id
                        return redirect('note_page')
                else:
                        alert="Yur are not an employee"
                        return render(req,'authentication/home.html',{'form':form,'alert':alert})
        else:
              form=Login(req.POST)  
        return render(req,'authentication/home.html',{'form':form})  
def terms_of_service(req):
      return render(req,'authentication/terms_of_service.html')
def privacy_policy(req):
      return render(req,'authentication/privacy_policy.html')
def SignUp_views(req):
      if req.method=='POST':
            form =SignUp(req.POST)
            if form.is_valid():
                  inp_name=form.cleaned_data['name']
                  inp_email=form.cleaned_data['email']
                  inp_password1=form.cleaned_data['password1']
                  inp_password2=form.cleaned_data['password2']
                  inp_terms=form.cleaned_data['terms']
                  if inp_terms and inp_password1==inp_password2:
                        Login.model.object.create(
                              name=inp_name,
                              email=inp_email,
                              password=inp_password1,
                        )
            
# Create your views here.
