
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from authentication.forms import Login, SignUp, Forget_Password
from authentication.models import Login_model


def home(req):
    return render(req, 'authentication/home.html')


def Login_views(req):
    if req.method == 'POST':
        form = Login(req.POST)
        if form.is_valid():
            inp_name = form.cleaned_data['name']
            inp_email = form.cleaned_data['email']
            inp_password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            matched_user = Login_model.objects.filter(
                name=inp_name, email=inp_email
            ).first()

            if matched_user and check_password(inp_password, matched_user.password):
                # Save session
                req.session['User_id'] = matched_user.id
                req.session['User_name'] = matched_user.name
                if remember_me:
                    req.session.set_expiry(1209600)  # 2 weeks
                else:
                    req.session.set_expiry(0)  # until browser close

                return redirect('add_note')  # Redirect to Add Note page
            else:
                alert = "Invalid username, email, or password."
                return render(req, 'authentication/home.html', {'form': form, 'alert': alert})
    else:
        form = Login()

    return render(req, 'authentication/home.html', {'form': form})


def SignUp_views(req):
    if req.method == 'POST':
        form = SignUp(req.POST)
        if form.is_valid():
            inp_name = form.cleaned_data['name']
            inp_email = form.cleaned_data['email']
            inp_password1 = form.cleaned_data['password1']
            inp_password2 = form.cleaned_data['password2']
            inp_terms = form.cleaned_data['terms']

            if not inp_terms:
                alert = "You must accept the Terms of Service."
                return render(req, 'authentication/signup.html', {'form': form, 'alert': alert})

            if inp_password1 != inp_password2:
                alert = "Passwords do not match."
                return render(req, 'authentication/signup.html', {'form': form, 'alert': alert})

            # Save hashed password
            hashed_pw = make_password(inp_password1)
            Login_model.objects.create(
                name=inp_name,
                email=inp_email,
                password=hashed_pw,
            )

            return redirect('login_page')  # Redirect to login after signup
    else:
        form = SignUp()

    return render(req, 'authentication/signup.html', {'form': form})


def Logout_views(req):
    req.session.flush()  # Clear session
    return redirect('login_page')


def terms_of_service(req):
    return render(req, 'authentication/terms_of_service.html')


def privacy_policy(req):
    return render(req, 'authentication/privacy_policy.html')
