from django.shortcuts import render
def home(req):
    return render(req,'application/home.html')
def about(req):
    return render(req,'application/about.html')
# Create your views here.
